#!/usr/bin/env python3
"""Fixed R232 resource installation; upstream scientific code is untouched."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile

SCHEMA = 'taffish.gtdbtk.r232.v1'
MANIFEST, FILES, READY = 'taffish-resource.json', 'taffish-resource.files', 'taffish-resource.ready'
CONTROL = {MANIFEST, FILES, READY}
RESOURCE = dict(identity='R232/232.0', filename='gtdbtk_r232_data.tar.gz',
    url='https://data.gtdb.ecogenomic.org/releases/release232/232.0/auxillary_files/gtdbtk_package/full_package/gtdbtk_r232_data.tar.gz',
    md5='25a59e0352b1fd150c589f56559767d4', size=60806405195, unpack_budget=110*1024**3,
    license='CC-BY-SA-4.0', license_url='https://gtdb.ecogenomic.org/licenses')

def require(condition, message):
    if not condition:
        raise ValueError(message)

def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(4*1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def regular(path):
    require(not path.is_symlink() and stat.S_ISREG(path.lstat().st_mode), 'not a regular file: '+str(path))

def safe_name(name):
    p = PurePosixPath(name)
    require(p.parts and not p.is_absolute() and '..' not in p.parts and
            all(re.fullmatch(r'[A-Za-z0-9_.+-]+', v) for v in p.parts), 'unsafe archive/inventory path: '+name)
    return p.parts

def inventory(root, full=True):
    result = {}
    for p in sorted(root.rglob('*')):
        require(not p.is_symlink(), 'resource contains symlink: '+str(p))
        require(not p.stat().st_mode & 0o022, 'resource is group/world writable: '+str(p))
        if p.is_dir():
            continue
        regular(p)
        name = p.relative_to(root).as_posix()
        safe_name(name)
        if name not in CONTROL:
            result[name] = dict(size=p.stat().st_size)
            if full:
                result[name]['sha256'] = digest(p)
    return result

def metadata(root):
    p = root/'metadata/metadata.txt'
    regular(p)
    values = dict(line.strip().split('=',1) for line in p.read_text().splitlines() if '=' in line)
    require(values.get('VERSION_DATA') == 'r232', 'expected R232 metadata')
    for key in ('RED_DIST_BAC_DICT','RED_DIST_ARC_DICT'):
        require(isinstance(json.loads(values[key]),dict), 'invalid RED metadata')

def verify(root, full=True, resource=None):
    resource = RESOURCE if resource is None else resource
    root = Path(root)
    require(root.is_dir() and not root.is_symlink() and not root.stat().st_mode & 0o022,
            'invalid physical database directory')
    for name in CONTROL:
        regular(root/name)
    require((root/READY).read_text().strip() == digest(root/MANIFEST)+' '+digest(root/FILES),
            'ready/manifest/inventory checksum mismatch')
    record = json.loads((root/MANIFEST).read_text())
    require(record['schema'] == SCHEMA and record['resource'] == resource, 'wrong fixed resource identity')
    require(record['files'], 'empty resource inventory')
    require((root/FILES).read_text() == ''.join('%s %s\n' % (v['size'],k) for k,v in sorted(record['files'].items())),
            'inventory differs from manifest')
    expected = record['files'] if full else {k:dict(size=v['size']) for k,v in record['files'].items()}
    require(inventory(root,full) == expected, 'database content differs from fixed inventory')
    metadata(root)
    return record

def seal(root, resource, provenance):
    for p in root.rglob('*'):
        require(not p.is_symlink(), 'cannot seal symlink member')
        p.chmod(0o755 if p.is_dir() else 0o644)
    metadata(root)
    record = dict(schema=SCHEMA,resource=resource,provenance=provenance,files=inventory(root))
    (root/MANIFEST).write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
    (root/FILES).write_text(''.join('%s %s\n' % (v['size'],k) for k,v in sorted(record['files'].items())))
    (root/READY).write_text(digest(root/MANIFEST)+' '+digest(root/FILES)+'\n')
    for name in CONTROL:
        (root/name).chmod(0o644)
    root.chmod(0o755)
    verify(root,resource=resource)

def obtain(resource, cache, source):
    blob, partial = cache/(resource['md5']+'.tar.gz'), cache/(resource['md5']+'.part')
    for p in (blob,partial):
        if os.path.lexists(p):
            regular(p)
    if blob.exists():
        require(blob.stat().st_size == resource['size'] and digest(blob,'md5') == resource['md5'],
                'corrupt completed cache; inspect/remove only this file: '+str(blob))
        return blob
    if source is not None:
        regular(source)
        require(not partial.exists(), 'partial retained; inspect/remove exact partial before local import: '+str(partial))
        with source.open('rb') as inp, partial.open('xb') as out:
            shutil.copyfileobj(inp,out)
    else:
        # 固定URL不保证永久可得；先区分网络/404/截断。只恢复同MD5字节，不追随latest或跳过校验。
        print('stage=download fixed R232; partial retained on failure',flush=True)
        result = subprocess.run(['curl','--fail','--location','--proto','=https','--proto-redir','=https',
            '--connect-timeout','30','--speed-limit','1024','--speed-time','120','--retry','2','--retry-delay','3',
            '--continue-at','-','--output',str(partial),resource['url']])
        require(result.returncode == 0, 'download failed exit=%s; partial retained: %s' % (result.returncode,partial))
    require(partial.stat().st_size == resource['size'] and digest(partial,'md5') == resource['md5'],
            'archive size/MD5 mismatch; partial retained: '+str(partial))
    partial.chmod(0o600)
    partial.rename(blob)
    return blob

def unpack(blob, stage, reserve):
    print('stage=unpack verified archive',flush=True)
    with tarfile.open(blob,'r:gz') as archive:
        members = archive.getmembers()
        require(shutil.disk_usage(stage).free > sum(m.size for m in members)+reserve, 'insufficient extraction space')
        seen, tops = set(), set()
        for m in members:
            parts = safe_name(m.name)
            tops.add(parts[0])
            require(parts[0] in ('release232','r232') and len(tops)==1, 'unexpected R232 archive root')
            require(m.isdir() or m.isfile(), 'archive link/device rejected: '+m.name)
            if len(parts)==1:
                require(m.isdir(), 'invalid archive root')
                continue
            name = '/'.join(parts[1:])
            require(name not in seen and name not in CONTROL, 'duplicate/reserved member: '+name)
            seen.add(name)
            p = stage.joinpath(*parts[1:])
            if m.isdir():
                p.mkdir(parents=True,exist_ok=True)
            else:
                p.parent.mkdir(parents=True,exist_ok=True)
                with archive.extractfile(m) as inp, p.open('xb') as out:
                    shutil.copyfileobj(inp,out)

def install(dbroot, source=None, resource=None, reserve=1024**3):
    resource = RESOURCE if resource is None else resource
    dbroot = Path(dbroot).absolute()
    require(dbroot.is_dir() and dbroot.resolve() == dbroot, 'create a physical --db-root directory first')
    require(not dbroot.stat().st_mode & 0o022, 'installation parent must not be group/world writable')
    final = dbroot/'r232'
    require(not final.is_symlink(), 'installation destination is a symlink; do not overwrite')
    fd = os.open(str(dbroot/'.r232.lock'),os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as handle:
        require(os.fstat(handle.fileno()).st_uid == os.geteuid() and
                stat.S_IMODE(os.fstat(handle.fileno()).st_mode)==0o600, 'unsafe install lock')
        fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if os.path.lexists(final):
            verify(final,resource=resource)
            print('already verified: '+str(final))
            return final
        cache = dbroot/'.r232.cache'
        cache.mkdir(mode=0o700,exist_ok=True)
        require(not cache.is_symlink() and cache.stat().st_uid == os.geteuid() and
                stat.S_IMODE(cache.stat().st_mode)==0o700, 'cache must be owned private 0700')
        needed = 0 if (cache/(resource['md5']+'.tar.gz')).exists() else resource['size']
        require(shutil.disk_usage(dbroot).free > needed+resource['unpack_budget']+reserve,
                'insufficient space: fixed archive + unpack budget + reserve required')
        stage = Path(tempfile.mkdtemp(prefix='.r232.stage-',dir=str(dbroot)))
        try:
            blob = obtain(resource,cache,source)
            unpack(blob,stage,reserve)
            seal(stage,resource,dict(method='verified-archive',archive_sha256=digest(blob)))
            require(not os.path.lexists(final), 'destination appeared; refusing replacement')
            stage.rename(final)
            stage = None
            print('installed and verified: '+str(final))
            return final
        finally:
            if stage is not None:
                shutil.rmtree(stage)

def main():
    p = argparse.ArgumentParser(description='Install the fixed GTDB-Tk R232 reference package atomically. No overwrite or latest lookup.')
    p.add_argument('--db-root',type=Path,default=Path.cwd(),help='existing physical host-bound parent; final directory is DBROOT/r232')
    p.add_argument('--source-archive',type=Path,help='offline import of exact official archive (same fixed MD5 and size)')
    p.add_argument('--dry-run',action='store_true')
    p.add_argument('--verify',action='store_true',help='full SHA256 inventory audit of DBROOT/r232; readonly, offline')
    p.add_argument('--verify-path',type=Path,help='full audit of an exact prepared resource path; root symlink resolved')
    a = p.parse_args()
    try:
        if a.dry_run:
            print(json.dumps(dict(resource=RESOURCE,destination=str(a.db_root/'r232'),reserve_bytes=1024**3,
                overwrite='refused; install in a new parent and explicitly switch',
                recovery='retry reuses verified cache; partial kept; inspect/remove only named corrupt partial',
                permissions='directories 0755, files 0644; install parent must not be group/world writable'),indent=2))
        elif a.verify or a.verify_path:
            root = (a.verify_path or a.db_root/'r232').resolve(strict=True)
            verify(root)
            print('verified R232: '+str(root))
        else:
            os.umask(0o022)
            install(a.db_root,a.source_archive)
    except Exception as e:
        print('gtdbtk-resources: '+str(e),file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':
    sys.exit(main())
