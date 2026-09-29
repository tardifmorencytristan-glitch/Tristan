from __future__ import annotations
import hashlib,json,os,pathlib,shutil,subprocess,time,socket
HOME=pathlib.Path.home()
SRC=HOME/"TristanRepos"/"Tristan"/"software"/"residual-operator-learning"
DST_W=HOME/".tristan"/"event-morphogenesis"/"watcher.pyw"
DST_L=HOME/".tristan"/"residual-operator-map"/"learner.pyw"
RUNTIME=HOME/".tristan"/"residual-operator-map"/"materializer"
RUNTIME.mkdir(parents=True,exist_ok=True)
PY=HOME/"AppData"/"Local"/"Programs"/"Python"/"Python313"/"python.exe"
PYW=PY.with_name("pythonw.exe")
def sha(p):
    h=hashlib.sha256();h.update(pathlib.Path(p).read_bytes());return h.hexdigest()
def compile_ok(p):
    try:return subprocess.run([str(PY),"-m","py_compile",str(p)],capture_output=True,timeout=30).returncode==0
    except:return False
def stop(pattern):
    q=f"""Get-CimInstance Win32_Process | Where-Object {{ $_.Name -match '^pythonw?\\.exe$' -and $_.CommandLine -like '*{pattern}*' }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }}"""
    subprocess.run(["powershell.exe","-NoProfile","-Command",q],capture_output=True)
def main():
    sw=SRC/"watcher.pyw";sl=SRC/"learner.pyw";manifest=SRC/"manifest.json"
    if not (sw.exists() and sl.exists() and manifest.exists()):return 2
    if not (compile_ok(sw) and compile_ok(sl)):return 3
    before={"watcher":sha(DST_W) if DST_W.exists() else None,"learner":sha(DST_L) if DST_L.exists() else None}
    after={"watcher":sha(sw),"learner":sha(sl)}
    if before==after:return 0
    stamp=time.strftime("%Y%m%d-%H%M%S");bak=RUNTIME/("backup-"+stamp);bak.mkdir(parents=True,exist_ok=True)
    if DST_W.exists():shutil.copy2(DST_W,bak/"watcher.pyw")
    if DST_L.exists():shutil.copy2(DST_L,bak/"learner.pyw")
    shutil.copy2(sw,DST_W);shutil.copy2(sl,DST_L)
    if not (compile_ok(DST_W) and compile_ok(DST_L)):
        if (bak/"watcher.pyw").exists():shutil.copy2(bak/"watcher.pyw",DST_W)
        if (bak/"learner.pyw").exists():shutil.copy2(bak/"learner.pyw",DST_L)
        return 4
    stop("event-morphogenesis\\watcher.pyw");stop("residual-operator-map\\learner.pyw")
    subprocess.Popen([str(PYW),str(DST_W)],creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0x08000000))
    subprocess.Popen([str(PYW),str(DST_L)],creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0x08000000))
    receipt={"schema":"tristan.residual_operator.materialization.r1","ts":time.time(),"node":socket.gethostname(),
      "source_version":json.loads(manifest.read_text(encoding="utf-8-sig")).get("version"),
      "before":before,"after":after,"backup":str(bak),"status":"PROMOTED"}
    (RUNTIME/"receipt-latest.json").write_text(json.dumps(receipt,indent=2),encoding="utf-8")
    return 0
if __name__=="__main__":raise SystemExit(main())
