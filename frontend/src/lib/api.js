import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({ baseURL, timeout: 20000 })

export const getSummary = () => api.get('/dashboard/summary').then((r) => r.data)
export const getAlerts = () => api.get('/dashboard/alerts').then((r) => r.data)
export const getRiskHeatmap = () => api.get('/dashboard/risk-heatmap').then((r) => r.data)
export const listPumps = () => api.get('/pump').then((r) => r.data)
export const getPump = (id, points = 300) =>
  api.get(`/pump/${id}`, { params: { points } }).then((r) => r.data)
export const getDrivers = () => api.get('/insights/drivers').then((r) => r.data)
export const getFeatureImportance = () =>
  api.get('/insights/feature-importance').then((r) => r.data)
export const getForecastMetrics = () =>
  api.get('/insights/forecast-metrics').then((r) => r.data)
export const reportUrl = (id) => `${baseURL}/pump/${id}/report`

export const ALERT_COLORS = {
  Normal: '#10b981',
  Warning: '#f59e0b',
  Critical: '#ef4444',
}
