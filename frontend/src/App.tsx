import { useEffect, useMemo, useState } from 'react'
import { Search, Sun, Moon, Monitor, Folder, FileText, Image, FileSpreadsheet, Film, LayoutDashboard, HardDrive, ChevronLeft, ChevronRight, RefreshCw, Cloud, Menu, X, Filter, ExternalLink, Upload, LogOut, BookOpen, Clock3, StickyNote, Bookmark, Download, Home, ArrowRight, Trash2 } from 'lucide-react'
import { api, uploadFile, FileRecord, Folder as FolderType, Source, getToken, setToken, downloadFile } from './lib/api'
import type { ReactNode, FormEvent } from 'react'

type Theme = 'light' | 'dark' | 'system'
const iconFor = (kind: string) => kind === 'image' ? Image : kind === 'spreadsheet' ? FileSpreadsheet : kind === 'video' ? Film : FileText
const formatBytes = (n: number) => { if (!n) return '0 B'; const u=['B','KB','MB','GB','TB']; const i=Math.min(Math.floor(Math.log(n)/Math.log(1024)),4); return `${(n/Math.pow(1024,i)).toFixed(i===0?0:1)} ${u[i]}` }
const importSummary = (c:any) => `تم فهرسة ${c.folders} مجلد و${c.files} ملف؛ تم نسخ ${c.downloaded_files} ملف إلى التخزين (${formatBytes(c.bytes_downloaded)})، وتُرك ${c.skipped_large + c.skipped_total_limit + c.google_native_files} ملفاً كرابط Drive أو بسبب حدود الحجم.`

export default function App() {
  const [token, setAuthToken] = useState<string | null>(() => getToken())
  const [theme, setTheme] = useState<Theme>((localStorage.getItem('le-cours-theme') as Theme) || 'system')
  const [sources, setSources] = useState<Source[]>([])
  const [folders, setFolders] = useState<FolderType[]>([])
  const [files, setFiles] = useState<FileRecord[]>([])
  const [stats, setStats] = useState<any>(null)
  const [selectedSource, setSelectedSource] = useState<number | undefined>()
  const [selectedFolder, setSelectedFolder] = useState<FolderType | null>(null)
  const [query, setQuery] = useState('')
  const [kind, setKind] = useState('')
  const [active, setActive] = useState<'dashboard'|'files'|'drive'>('dashboard')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [mobileNav, setMobileNav] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState('')
  const [driveUrl, setDriveUrl] = useState('')
  const [driveLabel, setDriveLabel] = useState('')
  const [driveBusy, setDriveBusy] = useState(false)

  useEffect(() => { localStorage.setItem('le-cours-theme', theme); document.documentElement.dataset.theme = theme }, [theme])
  const refresh = async () => {
    setLoading(true); setError('')
    try {
      const [s, d] = await Promise.all([api.sources(), api.dashboard()])
      setSources(s.results); setStats(d)
      const sourceId = selectedSource || s.results[0]?.id
      if (sourceId && !selectedSource) setSelectedSource(sourceId)
      const [f, allFiles] = await Promise.all([api.folders(sourceId), api.files(sourceId)])
      setFolders(f.results); setFiles(allFiles.results)
    } catch { setError('تعذر الاتصال بالـ API. تأكد أن Django يعمل وأن VITE_API_BASE_URL صحيح. يمكنك تشغيل seed_demo للبيانات التجريبية.') }
    finally { setLoading(false) }
  }
  useEffect(() => { if (token) refresh() }, [token])
  useEffect(() => { const handler = () => setAuthToken(null); window.addEventListener('le-cours:unauthorized', handler); return () => window.removeEventListener('le-cours:unauthorized', handler) }, [])
  useEffect(() => {
    if (!token || !selectedSource) return
    setSelectedFolder(null)
    Promise.all([api.folders(selectedSource), api.files(selectedSource)]).then(([f, fs]) => { setFolders(f.results); setFiles(fs.results) }).catch(() => {})
  }, [selectedSource])
  const visibleFiles = useMemo(() => files.filter(f => (!selectedFolder || f.folder === selectedFolder.id) && (!kind || f.kind === kind)), [files, selectedFolder, kind])
  const [results, setResults] = useState<FileRecord[] | null>(null)
  useEffect(() => {
    if (!query.trim()) { setResults(null); return }
    const t = setTimeout(() => api.search(query, selectedSource, kind || undefined).then(setResults).catch(() => setResults([])), 250)
    return () => clearTimeout(t)
  }, [query, selectedSource, kind])
  const shownFiles = results ?? visibleFiles
  const currentSource = sources.find(s => s.id === selectedSource)

  if (!token) return window.location.hash === '#admin' ? <Login onLogin={(newToken) => { setToken(newToken); setAuthToken(newToken) }} /> : <PublicLibrary onAdmin={() => { window.location.hash = 'admin'; window.location.reload() }} />

  return <div className="app-shell">
    <aside className={`sidebar ${mobileNav?'open':''}`}>
      <div className="brand"><div className="brand-mark">و</div><div><strong>L-E-COURS</strong><small>إدارة ملفاتك ببساطة</small></div><button className="mobile-close" onClick={()=>setMobileNav(false)}><X size={18}/></button></div>
      <div className="nav-label">القائمة الرئيسية</div>
      <button className={`nav-item ${active==='dashboard'?'active':''}`} onClick={()=>{setActive('dashboard');setMobileNav(false)}}><LayoutDashboard size={18}/> لوحة التحكم</button>
      <button className={`nav-item ${active==='files'?'active':''}`} onClick={()=>{setActive('files');setMobileNav(false)}}><Folder size={18}/> الملفات والمجلدات</button>
      <button className={`nav-item ${active==='drive'?'active':''}`} onClick={()=>{setActive('drive');setMobileNav(false)}}><Cloud size={18}/> ربط Google Drive</button>
      <div className="nav-label source-label">مصادر التخزين <span>{sources.length}</span></div>
      {sources.map(s=><button key={s.id} className={`source-item ${selectedSource===s.id?'selected':''}`} onClick={()=>{setSelectedSource(s.id);setActive('files')}}><span className="source-dot" style={{background:s.color}}/><span>{s.label || s.name}</span><small>{s.file_count}</small></button>)}
      <div className="sidebar-bottom"><div className="storage-card"><div className="storage-icon"><Cloud size={18}/></div><strong>L-E-COURS Workspace</strong><p>مساحة موحدة لمصادرك</p><div className="storage-track"><span style={{width:'38%'}}/></div><small>نسخة تجريبية · بيانات محلية</small></div><div className="profile-row"><div className="avatar">W</div><div><b>مساحة العمل</b><small>مدير النظام</small></div><span className="online-dot"/></div></div>
    </aside>
    {mobileNav && <div className="scrim" onClick={()=>setMobileNav(false)}/>}
    <main className="main-area">
      <header className="topbar"><div className="top-left"><button className="icon-btn menu-btn" onClick={()=>setMobileNav(true)}><Menu size={20}/></button><div className="breadcrumb">L-E-COURS <ChevronLeft size={14}/> <span>{active==='dashboard'?'لوحة التحكم':active==='drive'?'ربط Google Drive':'الملفات والمجلدات'}</span></div></div><div className="top-actions"><div className="theme-switch" title="مظهر الواجهة"><button className={theme==='light'?'chosen':''} onClick={()=>setTheme('light')}><Sun size={16}/></button><button className={theme==='dark'?'chosen':''} onClick={()=>setTheme('dark')}><Moon size={16}/></button><button className={theme==='system'?'chosen':''} onClick={()=>setTheme('system')}><Monitor size={16}/></button></div><button className="icon-btn" onClick={refresh} title="تحديث"><RefreshCw size={17}/></button><button className="icon-btn" title="تسجيل الخروج" onClick={()=>{api.logout().catch(()=>{}).finally(()=>{setToken(null);setAuthToken(null);window.location.hash=''})}}><LogOut size={17}/></button><div className="avatar small-avatar">L</div></div></header>
      <div className="page-content">
        <section className="welcome-row"><div><div className="eyebrow">مساحة العمل الخاصة بك</div><h1>{active==='dashboard'?'كل ملفاتك، في مكان واحد':active==='drive'?'أضف مصدراً جديداً':'الملفات والمجلدات'}</h1><p>نظّم، استكشف وابحث في مصادر التخزين المتصلة.</p></div><div className="welcome-actions">{active!=='drive' && <label className="primary-btn upload-btn"><Upload size={17}/>{uploading?'جارٍ الرفع...':'رفع ملف'}<input type="file" hidden disabled={uploading || !selectedSource} onChange={async e=>{const file=e.target.files?.[0];if(!file||!selectedSource)return;setUploading(true);setUploadMessage('');try{await uploadFile(file,selectedSource,selectedFolder?.id);setUploadMessage('تم رفع الملف بنجاح');await refresh()}catch(err){setUploadMessage(err instanceof Error?err.message:'فشل رفع الملف')}finally{setUploading(false);e.target.value=''}}}/></label>}<button className="secondary-btn" onClick={()=>setActive(active==='drive'?'files':'drive')}><Cloud size={17}/> {active==='drive'?'العودة للملفات':'إضافة Google Drive'}</button></div></section>
        {error && <div className="error-banner">{error}</div>}{uploadMessage && <div className="success-banner">{uploadMessage}</div>}
        {active==='drive' && <section className="panel drive-import-panel"><div className="panel-heading"><div><h2>إضافة مجلد Google Drive</h2><p>كل مجلد رئيسي داخل الرابط يتحول تلقائياً إلى شعبة مستقلة.</p></div><Cloud size={24}/></div><form className="drive-import-form" onSubmit={async e=>{e.preventDefault();setDriveBusy(true);setError('');setUploadMessage('');try{const result=await api.addDriveSource(driveUrl,driveLabel);setUploadMessage(`تمت إضافة ${result.source.label}. ${importSummary(result.imported)}`);setDriveUrl('');setDriveLabel('');await refresh()}catch(err){setError(err instanceof Error?err.message:'تعذر استيراد رابط Google Drive')}finally{setDriveBusy(false)}}}><label>اسم مجموعة Drive (اختياري)<input value={driveLabel} onChange={e=>setDriveLabel(e.target.value)} placeholder="مثلاً: كلية العلوم" /></label><label>رابط مجلد Google Drive<input type="url" required value={driveUrl} onChange={e=>setDriveUrl(e.target.value)} placeholder="https://drive.google.com/drive/folders/..." /></label><div className="drive-import-note">يجب ضبط GOOGLE_DRIVE_API_KEY في إعدادات الخادم، وأن تكون صلاحية المجلد: Anyone with the link — Viewer.</div><button className="primary-btn" disabled={driveBusy}>{driveBusy?'جارٍ فحص واستيراد المجلدات...':'استيراد المجلدات والملفات'}</button></form><div className="source-cards">{sources.filter(s=>s.drive_url).map(s=><div className="source-card" key={s.id}><div className="drive-icon"><HardDrive size={20}/></div><div className="source-card-text"><b>{s.label||s.name}</b><small>{s.sync_status==='success'?'تمت المزامنة':s.sync_status==='error'?'خطأ في المزامنة':'بانتظار المزامنة'} · {s.file_count} ملف</small></div><button className="text-btn" onClick={async()=>{try{const r=await api.syncDriveSource(s.id);setUploadMessage(importSummary(r.imported));await refresh()}catch(err){setError(err instanceof Error?err.message:'فشل التحديث')}}}><RefreshCw size={15}/> مزامنة</button></div>)}</div></section>}
        {active==='dashboard' && <><section className="stats-grid">
          <Stat icon={<HardDrive/>} label="مصادر التخزين" value={stats?.sources ?? '—'} tone="blue"/>
          <Stat icon={<Folder/>} label="إجمالي المجلدات" value={stats?.folders ?? '—'} tone="violet"/>
          <Stat icon={<FileText/>} label="إجمالي الملفات" value={stats?.files ?? '—'} tone="green"/>
          <Stat icon={<Cloud/>} label="الحجم الإجمالي" value={stats?formatBytes(stats.total_size_bytes):'—'} tone="orange"/>
        </section>
        <section className="content-grid"><div className="panel source-panel"><div className="panel-heading"><div><h2>مصادر التخزين</h2><p>المصادر المسجلة في مساحة العمل</p></div><span className="subtle-count">{sources.length} مصادر</span></div>
          <div className="source-cards">{sources.map(s=><button key={s.id} className="source-card" onClick={()=>{setSelectedSource(s.id);setActive('files')}}><div className="drive-icon" style={{background:`${s.color}18`,color:s.color}}><HardDrive size={21}/></div><div className="source-card-text"><b>{s.label||s.name}</b><small>{s.folder_count} مجلد · {s.file_count} ملف</small></div><ChevronLeft size={17} className="muted-icon"/></button>)}
          {!sources.length && <Empty text="لا توجد مصادر بعد. شغّل seed_demo لعرض بيانات تجريبية."/>}</div></div>
          <div className="panel quick-panel"><div className="panel-heading"><div><h2>الوصول السريع</h2><p>ابدأ من هنا</p></div></div><button className="quick-action" onClick={()=>setActive('files')}><div className="quick-icon"><Folder size={19}/></div><span><b>تصفح المجلدات</b><small>استكشف الهيكل والمحتوى</small></span><ChevronLeft size={17}/></button><button className="quick-action" onClick={()=>document.getElementById('global-search')?.focus()}><div className="quick-icon purple"><Search size={19}/></div><span><b>البحث عن ملف</b><small>ابحث بالاسم أو النوع</small></span><ChevronLeft size={17}/></button></div></section>
        </>}
        {active!=='drive' && <section className="panel files-panel"><div className="panel-heading files-heading"><div><h2>{active==='dashboard'?'أحدث الملفات':'استعراض الملفات'}</h2><p>{selectedFolder?`داخل مجلد ${selectedFolder.name}`:currentSource?.label||'جميع الملفات في المصدر المحدد'}</p></div><button className="text-btn" onClick={()=>setActive('files')}>عرض الكل <ChevronLeft size={15}/></button></div>
          <div className="toolbar"><div className="search-box"><Search size={17}/><input id="global-search" value={query} onChange={e=>setQuery(e.target.value)} placeholder="ابحث عن ملف أو مستند..."/>{query&&<button onClick={()=>setQuery('')}><X size={15}/></button>}</div><div className="filter-box"><Filter size={16}/><select value={kind} onChange={e=>setKind(e.target.value)}><option value="">كل الأنواع</option><option value="pdf">PDF</option><option value="image">صور</option><option value="document">مستندات</option><option value="spreadsheet">جداول</option><option value="video">فيديو</option><option value="other">أخرى</option></select></div></div>
          {active==='files' && <div className="folder-strip"><button className={!selectedFolder?'folder-chip active-chip':'folder-chip'} onClick={()=>setSelectedFolder(null)}>كل المجلدات</button>{folders.map(f=><button key={f.id} className={selectedFolder?.id===f.id?'folder-chip active-chip':'folder-chip'} onClick={()=>setSelectedFolder(f)}><Folder size={14}/>{f.name}<small>{f.files_count}</small></button>)}</div>}
          <div className="table-wrap"><table><thead><tr><th>اسم الملف</th><th>المجلد</th><th>المصدر</th><th>الحجم</th><th>النوع</th><th></th></tr></thead><tbody>
            {shownFiles.slice(0, active==='dashboard'?6:100).map(file=>{const Icon=iconFor(file.kind);return <tr key={file.id}><td><div className="file-name"><span className={`file-icon ${file.kind}`}><Icon size={17}/></span><b>{file.name}</b></div></td><td>{file.folder_name||'—'}</td><td><span className="table-source"><i style={{background:sources.find(s=>s.id===file.source)?.color||'#888'}}/>{file.source_name}</span></td><td className="numeric">{file.size_display||formatBytes(file.size_bytes)}</td><td><span className={`type-pill ${file.kind}`}>{file.kind}</span></td><td>{file.has_upload?<button className="open-link" title="تحميل الملف" onClick={()=>downloadFile(file.id,file.name).catch(err=>setError(err.message))}><ExternalLink size={15}/></button>:file.web_url?<a className="open-link" href={file.web_url} target="_blank" rel="noreferrer"><ExternalLink size={15}/></a>:<span className="muted-icon">—</span>}</td></tr>})}
            {!shownFiles.length && <tr><td colSpan={6}><Empty text={loading?'جارٍ التحميل...':'لا توجد ملفات مطابقة.'}/></td></tr>}
          </tbody></table></div><div className="table-footer"><span>عرض {shownFiles.length} ملف</span><span>الملفات التجريبية بيانات وصفية فقط</span></div>
        </section>}
        <footer className="footer"><span>L-E-COURS © 2026</span><span>منصة موحدة لإدارة الملفات</span></footer>
      </div>
    </main>
  </div>
}
function Stat({icon,label,value,tone}:{icon:ReactNode,label:string,value:string|number,tone:string}) { return <div className="stat-card"><div className={`stat-icon ${tone}`}>{icon}</div><div><small>{label}</small><strong>{value}</strong></div><span className="stat-decoration"/></div> }
function Empty({text}:{text:string}) { return <div className="empty-state">{text}</div> }



function PublicLibrary({onAdmin}:{onAdmin:()=>void}) {
  const [sources,setSources]=useState<Source[]>([])
  const [catalogue,setCatalogue]=useState<any[]>([])
  const [folders,setFolders]=useState<FolderType[]>([])
  const [files,setFiles]=useState<FileRecord[]>([])
  const [source,setSource]=useState<number|undefined>()
  const [folder,setFolder]=useState<FolderType|null>(null)
  const [folderStack,setFolderStack]=useState<FolderType[]>([])
  const [query,setQuery]=useState('')
  const [favorites,setFavorites]=useState<number[]>(()=>JSON.parse(localStorage.getItem('le-cours-favorites')||'[]'))
  const [showFavorites,setShowFavorites]=useState(false)
  const [showRecent,setShowRecent]=useState(false)
  const [recent,setRecent]=useState<FileRecord[]>(()=>JSON.parse(localStorage.getItem('le-cours-recent')||'[]'))
  const [notes,setNotes]=useState<Record<number,string>>(()=>JSON.parse(localStorage.getItem('le-cours-notes')||'{}'))
  const [preview,setPreview]=useState<FileRecord|null>(null)
  const [noteTarget,setNoteTarget]=useState<FileRecord|null>(null)
  const [noteDraft,setNoteDraft]=useState('')
  const [loading,setLoading]=useState(true)
  const [error,setError]=useState('')
  const [theme,setTheme]=useState<Theme>((localStorage.getItem('le-cours-theme') as Theme)||'system')
  useEffect(()=>{document.documentElement.dataset.theme=theme;localStorage.setItem('le-cours-theme',theme)},[theme])
  useEffect(()=>{Promise.all([api.sources(),api.academic()]).then(async ([r,tree])=>{setSources(r.results);setCatalogue(tree);const first=r.results[0];if(first){setSource(first.id);const [f,fs]=await Promise.all([api.folders(first.id,null),api.files(first.id)]);setFolders(f.results);setFiles(fs.results)}}).catch(e=>setError(e.message||'تعذر تحميل المكتبة')).finally(()=>setLoading(false))},[])
  const chooseSource=async(id:number)=>{setSource(id);setFolder(null);setFolderStack([]);setQuery('');setShowFavorites(false);setLoading(true);try{const [f,fs]=await Promise.all([api.folders(id,null),api.files(id)]);setFolders(f.results);setFiles(fs.results)}catch(e){setError('تعذر تحميل محتوى الشعبة')}finally{setLoading(false)}}
  const chooseFolder=async(item:FolderType|null)=>{if(!source)return;const nextStack=item?[...folderStack,item]:[];setFolderStack(nextStack);setFolder(item);setLoading(true);try{const [f,fs]=await Promise.all([api.folders(source,item?.id??null),api.files(source,item?.id)]);setFolders(f.results);setFiles(fs.results)}catch{setError('تعذر تحميل المجلد')}finally{setLoading(false)}}
  const goBack=async()=>{if(!source)return;if(folderStack.length<=1){await chooseFolder(null);return}const next=folderStack.slice(0,-1);const parent=next[next.length-1];setFolderStack(next);setFolder(parent);setLoading(true);try{const [f,fs]=await Promise.all([api.folders(source,parent.id),api.files(source,parent.id)]);setFolders(f.results);setFiles(fs.results)}catch{setError('تعذر تحميل المجلد')}finally{setLoading(false)}}
  const chooseBreadcrumb=async(item:FolderType,index:number)=>{if(!source)return;setFolderStack(folderStack.slice(0,index+1));setFolder(item);setLoading(true);try{const [f,fs]=await Promise.all([api.folders(source,item.id),api.files(source,item.id)]);setFolders(f.results);setFiles(fs.results)}catch{setError('تعذر تحميل المجلد')}finally{setLoading(false)}}
  const toggleFavorite=(id:number)=>setFavorites(current=>{const next=current.includes(id)?current.filter(x=>x!==id):[...current,id];localStorage.setItem('le-cours-favorites',JSON.stringify(next));return next})
  const openFile=(file:FileRecord)=>{
    const next=[file,...recent.filter(x=>x.id!==file.id)].slice(0,12)
    setRecent(next);localStorage.setItem('le-cours-recent',JSON.stringify(next))
    const isPdf=file.kind==='pdf'||file.mime_type==='application/pdf'||file.name.toLowerCase().endsWith('.pdf')
    if(isPdf&&file.has_upload){setPreview(file);return}
    if(file.web_url){window.open(file.web_url,'_blank','noopener,noreferrer');return}
    if(file.has_upload){window.open(api.downloadUrl(file.id),'_blank','noopener,noreferrer');return}
    setError('المعاينة غير متاحة لهذا الملف حالياً.')
  }
  const openNote=(file:FileRecord)=>{setNoteTarget(file);setNoteDraft(notes[file.id]||'')}
  const saveNote=()=>{if(!noteTarget)return;const next={...notes,[noteTarget.id]:noteDraft};setNotes(next);localStorage.setItem('le-cours-notes',JSON.stringify(next));setNoteTarget(null)}
  const clearRecent=()=>{setRecent([]);localStorage.removeItem('le-cours-recent')}
  const levelLabel = folderStack.length===0 ? 'الشعب الرئيسية' : folderStack.length===1 ? 'المستويات الدراسية' : folderStack.length===2 ? 'المواد' : folderStack.length===3 ? 'الدروس' : 'المجلدات والملفات'
  const shown=files.filter(f=>(!query||f.name.toLowerCase().includes(query.toLowerCase()))&&(!showFavorites||favorites.includes(f.id)))
  const doGlobalSearch=async(value:string)=>{setQuery(value);if(value.trim()){setLoading(true);try{const results=await api.search(value);setFiles(results);setFolders([]);setFolder(null);setFolderStack([])}catch{setError('تعذر البحث')}finally{setLoading(false)}}else if(source){chooseFolder(folder)}}
  return <div className="public-shell" dir="rtl">
    <header className="public-header"><div className="brand"><div className="brand-mark">ل</div><div><strong>L-E-COURS</strong><small>مكتبتك الرقمية</small></div></div><div className="top-actions"><div className="theme-switch"><button className={theme==='light'?'chosen':''} onClick={()=>setTheme('light')} title="فاتح"><Sun size={16}/></button><button className={theme==='dark'?'chosen':''} onClick={()=>setTheme('dark')} title="داكن"><Moon size={16}/></button><button className={theme==='system'?'chosen':''} onClick={()=>setTheme('system')} title="النظام"><Monitor size={16}/></button></div><button className="secondary-btn" onClick={onAdmin}>دخول الإدارة</button></div></header>
    <main className="public-content">
      <div className="public-hero"><span className="eyebrow">OPEN DIGITAL LIBRARY</span><h1>كل دروسك وملفاتك في مكان واحد</h1><p>تصفح الشعب والمستويات والمواد، اقرأ ملفاتك وسجّل ملاحظاتك وارجع لآخر ما فتحته.</p><div className="public-hero-meta"><span><BookOpen size={15}/> {catalogue.length} شعبة أكاديمية</span><span><Bookmark size={15}/> {favorites.length} مفضلة</span><span><Clock3 size={15}/> {recent.length} ملفات حديثة</span></div></div>
      <section className="public-layout"><aside className="panel public-sections"><h2>مصادر المحتوى</h2>{sources.map(s=><button key={s.id} className={source===s.id?'source-item selected':'source-item'} onClick={()=>chooseSource(s.id)}><span className="source-dot" style={{background:s.color}}/>{s.label||s.name}<small>{s.file_count}</small></button>)}{!sources.length&&!loading&&<Empty text="لا توجد شعب منشورة حالياً."/>}<div className="personal-tools"><h3>مساحتي على هذا الجهاز</h3><button onClick={async()=>{setShowFavorites(true);setShowRecent(false);setQuery('');if(source){setLoading(true);try{const all=await api.files(source);setFiles(all.results)}catch{setError('تعذر تحميل المفضلة')}finally{setLoading(false)}}}}><Bookmark size={16}/> المفضلة <span>{favorites.length}</span></button><button onClick={()=>{setShowRecent(true);setShowFavorites(false)}}><Clock3 size={16}/> آخر الملفات <span>{recent.length}</span></button><small>الملاحظات والمفضلة محفوظة محلياً في هذا المتصفح، دون حساب.</small></div></aside>
      <div className="panel public-browser"><div className="public-browser-head"><div><h2>{showRecent?'آخر الملفات المفتوحة':showFavorites?'ملفاتي المفضلة':folder?.name||sources.find(s=>s.id===source)?.label||'استكشف المكتبة'}</h2><p>{showRecent?'يمكنك الرجوع بسرعة إلى الملفات التي فتحتها مؤخراً':showFavorites?'ملفاتك المحفوظة على هذا الجهاز':folder?'محتويات المجلد':'اختر مجلداً أو افتح أحد الملفات'}</p></div>{(folder||showFavorites||showRecent)&&<button className="text-btn" onClick={()=>{if(showRecent||showFavorites){setShowRecent(false);setShowFavorites(false);if(source)chooseFolder(folder)}else goBack()}}><ChevronRight size={16}/> رجوع</button>}</div>
        {!showRecent&&<div className="search-box public-search"><Search size={17}/><input value={query} onChange={e=>doGlobalSearch(e.target.value)} placeholder="ابحث في جميع الشعب والملفات..."/><button className={showFavorites?'chosen':''} onClick={async()=>{const next=!showFavorites;setShowFavorites(next);setShowRecent(false);if(next&&source){setLoading(true);try{const all=await api.files(source);setFiles(all.results)}catch{setError('تعذر تحميل المفضلة')}finally{setLoading(false)}}else if(!next&&source){chooseFolder(folder)}}} title="عرض المفضلة">★ {favorites.length}</button></div>}
        {!showRecent&&!showFavorites&&folderStack.length>0&&<nav className="public-breadcrumbs"><button onClick={()=>chooseFolder(null)}><Home size={14}/> المكتبة</button>{folderStack.map((item,index)=><span key={item.id}><ChevronLeft size={13}/><button className={index===folderStack.length-1?'current':''} onClick={()=>chooseBreadcrumb(item,index)}>{item.name}</button></span>)}</nav>}
        {showRecent?<div className="public-file-list">{recent.map(file=><PublicFileRow key={file.id} file={file} favorite={favorites.includes(file.id)} hasNote={!!notes[file.id]} onOpen={()=>openFile(file)} onFavorite={()=>toggleFavorite(file.id)} onNote={()=>openNote(file)}/>)}{!recent.length&&<Empty text="لم تفتح أي ملف بعد."/>}<button className="text-btn clear-recent" onClick={clearRecent}><Trash2 size={14}/> مسح السجل</button></div>:<>
          {folders.length>0&&!showFavorites&&<><h3 className="public-section-title">{levelLabel}</h3><div className="public-folder-grid">{folders.map(f=><button className="public-folder" key={f.id} onClick={()=>chooseFolder(f)}><Folder size={23}/><b>{f.name}</b><small>{f.children_count} مجلدات · {f.files_count} ملفات</small></button>)}</div></>}
          <div className="public-file-list">{shown.map(file=><PublicFileRow key={file.id} file={file} favorite={favorites.includes(file.id)} hasNote={!!notes[file.id]} onOpen={()=>openFile(file)} onFavorite={()=>toggleFavorite(file.id)} onNote={()=>openNote(file)}/>)}{!shown.length&&!folders.length&&<Empty text={loading?'جارٍ تحميل المحتوى...':showFavorites?'لا توجد ملفات مفضلة في هذا الجهاز.':'لا توجد ملفات في هذا القسم حالياً.'}/>}</div>
        </>}
        {error&&<div className="error-banner">{error}<button className="open-link" onClick={()=>setError('')}>إغلاق</button></div>}
      </div></section>
    </main><footer className="footer public-footer">L-E-COURS © 2026 · مكتبة رقمية مفتوحة للجميع</footer>
    {preview&&<div className="reader-overlay" role="dialog" aria-modal="true" aria-label="قارئ PDF"><div className="reader-modal"><header><div><BookOpen size={19}/><strong>{preview.name}</strong></div><div><button className="reader-action" onClick={()=>openNote(preview)}><StickyNote size={16}/> ملاحظاتي</button><a className="reader-action" href={api.downloadUrl(preview.id)} target="_blank" rel="noreferrer"><Download size={16}/> تحميل</a><button className="reader-close" onClick={()=>setPreview(null)} aria-label="إغلاق"><X size={20}/></button></div></header><iframe title={`قارئ ${preview.name}`} src={api.downloadUrl(preview.id)} /></div></div>}
    {noteTarget&&<div className="reader-overlay note-overlay" role="dialog" aria-modal="true" aria-label="ملاحظاتي"><form className="note-modal" onSubmit={e=>{e.preventDefault();saveNote()}}><div className="note-heading"><div><StickyNote size={19}/><strong>ملاحظاتي الخاصة</strong></div><button type="button" className="reader-close" onClick={()=>setNoteTarget(null)}><X size={19}/></button></div><p>{noteTarget.name}</p><textarea value={noteDraft} onChange={e=>setNoteDraft(e.target.value)} placeholder="اكتب ملخصك، الأسئلة أو النقاط المهمة لهذا الملف..." rows={8}/><small>هذه الملاحظات محفوظة في هذا المتصفح فقط ولا تُرفع إلى الخادم.</small><div className="note-actions"><button type="button" className="secondary-btn" onClick={()=>setNoteTarget(null)}>إلغاء</button><button className="primary-btn" type="submit">حفظ الملاحظات</button></div></form></div>}
  </div>
}

function PublicFileRow({file,favorite,hasNote,onOpen,onFavorite,onNote}:{file:FileRecord;favorite:boolean;hasNote:boolean;onOpen:()=>void;onFavorite:()=>void;onNote:()=>void}) {
  const Icon=iconFor(file.kind)
  return <div className="public-file"><span className={`file-icon ${file.kind}`}><Icon size={18}/></span><div><b>{file.name}</b><small>{file.size_display} · {file.kind.toUpperCase()}</small></div><button className="open-link row-icon" title={favorite?'إزالة من المفضلة':'إضافة للمفضلة'} onClick={onFavorite}>{favorite?'★':'☆'}</button><button className={`open-link row-icon ${hasNote?'has-note':''}`} title="ملاحظاتي" onClick={onNote}><StickyNote size={16}/></button><button className="open-link" onClick={onOpen}>{file.kind==='pdf'?'قراءة':'فتح'} <ExternalLink size={14}/></button></div>
}

function Login({onLogin}:{onLogin:(token:string)=>void}) {
  const [username,setUsername]=useState('')
  const [password,setPassword]=useState('')
  const [busy,setBusy]=useState(false)
  const [error,setError]=useState('')
  const submit=async(e:FormEvent)=>{e.preventDefault();setBusy(true);setError('');try{const result=await api.login(username,password);onLogin(result.token)}catch{setError('اسم المستخدم أو كلمة المرور غير صحيحة، أو تعذر الاتصال بالخادم.')}finally{setBusy(false)}}
  return <div className="login-shell" dir="rtl"><form className="login-card" onSubmit={submit}><div className="brand-mark login-mark">ل</div><h1>L-E-COURS</h1><p>سجّل الدخول لإدارة ملفاتك بأمان</p>{error&&<div className="error-banner">{error}</div>}<label>اسم المستخدم<input autoComplete="username" value={username} onChange={e=>setUsername(e.target.value)} required /></label><label>كلمة المرور<input type="password" autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)} required /></label><button className="primary-btn" disabled={busy}>{busy?'جارٍ تسجيل الدخول...':'تسجيل الدخول'}</button><small>أنشئ حساب المدير أولاً عبر أمر createsuperuser في Django.</small><a href="/" className="text-btn">العودة إلى المكتبة العامة</a></form></div>
}
