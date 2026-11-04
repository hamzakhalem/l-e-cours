const API = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'
const TOKEN_KEY = 'le_cours_token'
export const adminUrl = `${API.replace(/\/api\/?$/, '')}/admin/`
export type Source = { id: number; name: string; label: string; color: string; is_active: boolean; is_public: boolean; drive_url: string; sync_status: string; sync_error: string; last_synced_at: string | null; folder_count: number; file_count: number }
export type Folder = { id: number; source: number; source_name: string; name: string; parent: number | null; children_count: number; files_count: number }
export type FileRecord = { id: number; source: number; source_name: string; folder: number | null; folder_name: string; resource_category?: number | null; name: string; kind: string; mime_type: string; size_bytes: number; size_display: string; modified_at: string | null; web_url: string; has_upload?: boolean; sha256?: string }
export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (token: string | null) => token ? localStorage.setItem(TOKEN_KEY, token) : localStorage.removeItem(TOKEN_KEY)

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  const token = getToken()
  if (token) headers.set('Authorization', `Token ${token}`)
  if (!(init.body instanceof FormData) && init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
  const response = await fetch(`${API}${path}`, { ...init, headers })
  if (!response.ok) {
    if (response.status === 401) {
      setToken(null)
      window.dispatchEvent(new Event('le-cours:unauthorized'))
    }
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || `API error ${response.status}`)
  }
  return response.json()
}

export const api = {
  login: (username: string, password: string) => request<{token: string}>('/auth/token/', { method: 'POST', body: JSON.stringify({username, password}) }),
  logout: () => request<{detail: string}>('/auth/logout/', { method: 'POST' }),
  dashboard: () => request<any>('/dashboard/'),
  academic: () => request<any[]>('/academic/'),
  sources: () => request<{results: Source[]}>('/sources/'),
  folders: (source?: number, parent?: number | null) => {
    const p = new URLSearchParams()
    if (source) p.set('source', String(source))
    if (parent !== undefined) p.set('parent', parent === null ? 'null' : String(parent))
    return request<{results: Folder[]}>(`/folders/?${p.toString()}`)
  },
  files: (source?: number, folder?: number) => {
    const p = new URLSearchParams()
    if (source) p.set('source', String(source))
    if (folder) p.set('folder', String(folder))
    return request<{results: FileRecord[]}>(`/files/?${p.toString()}`)
  },
  search: (q: string, source?: number, kind?: string) => {
    const p = new URLSearchParams({q})
    if (source) p.set('source', String(source))
    if (kind) p.set('kind', kind)
    return request<FileRecord[]>(`/search/?${p.toString()}`)
  },
  addDriveSource: (drive_url: string, label: string) => request<any>('/admin/drive-sources/', { method: 'POST', body: JSON.stringify({ drive_url, label }) }),
  syncDriveSource: (id: number) => request<any>(`/admin/drive-sources/${id}/sync/`, { method: 'POST' }),
  downloadUrl: (id: number) => `${API}/files/${id}/download/`,
}

export async function uploadFile(file: File, source: number, folder?: number, resourceCategory?: number): Promise<FileRecord> {
  const form = new FormData()
  form.append('file', file)
  form.append('source', String(source))
  if (folder) form.append('folder', String(folder))
  if (resourceCategory) form.append('resource_category', String(resourceCategory))
  return request<FileRecord>('/files/upload/', { method: 'POST', body: form })
}

export async function downloadFile(id: number, filename: string): Promise<void> {
  const token = getToken()
  const response = await fetch(`${API}/files/${id}/download/`, { headers: token ? { Authorization: `Token ${token}` } : {} })
  if (!response.ok) throw new Error('تعذر تحميل الملف.')
  const blob = await response.blob()
  const objectUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(objectUrl)
}
