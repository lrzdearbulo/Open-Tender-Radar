import { useState, useEffect } from 'react'
import TenderTable from './components/TenderTable'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [tenders, setTenders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({
    country: '',
    sector: '',
    sortBy: 'score',
    sortOrder: 'desc',
    page: 1,
    pageSize: 20
  })
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    pageSize: 20
  })
  const [countries, setCountries] = useState([])
  const [sectors, setSectors] = useState([])

  // Cargar países y sectores disponibles
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [countriesRes, sectorsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/countries`),
          fetch(`${API_BASE_URL}/sectors`)
        ])
        const countriesData = await countriesRes.json()
        const sectorsData = await sectorsRes.json()
        setCountries(countriesData.countries || [])
        setSectors(sectorsData.sectors || [])
      } catch (err) {
        console.error('Error loading options:', err)
      }
    }
    fetchOptions()
  }, [])

  // Cargar licitaciones
  useEffect(() => {
    const fetchTenders = async () => {
      setLoading(true)
      setError(null)
      
      try {
        const params = new URLSearchParams()
        if (filters.country) params.append('country', filters.country)
        if (filters.sector) params.append('sector', filters.sector)
        params.append('sort_by', filters.sortBy)
        params.append('sort_order', filters.sortOrder)
        params.append('page', filters.page.toString())
        params.append('page_size', filters.pageSize.toString())

        const response = await fetch(`${API_BASE_URL}/tenders?${params}`)
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        setTenders(data.items || [])
        setPagination({
          total: data.total || 0,
          page: data.page || 1,
          pageSize: data.page_size || 20
        })
      } catch (err) {
        setError(err.message)
        console.error('Error fetching tenders:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchTenders()
  }, [filters])

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: 1 // Reset to first page when filters change
    }))
  }

  const handlePageChange = (newPage) => {
    setFilters(prev => ({ ...prev, page: newPage }))
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">OpenTender Radar</h1>
          <p className="mt-2 text-sm text-gray-600">
            Herramienta para descubrir y evaluar licitaciones públicas con scoring de encaje
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filtros */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Filtros</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label htmlFor="country" className="block text-sm font-medium text-gray-700 mb-1">
                País
              </label>
              <select
                id="country"
                value={filters.country}
                onChange={(e) => handleFilterChange('country', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Todos los países</option>
                {countries.map(country => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="sector" className="block text-sm font-medium text-gray-700 mb-1">
                Sector
              </label>
              <select
                id="sector"
                value={filters.sector}
                onChange={(e) => handleFilterChange('sector', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Todos los sectores</option>
                {sectors.map(sector => (
                  <option key={sector} value={sector}>{sector}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="sortBy" className="block text-sm font-medium text-gray-700 mb-1">
                Ordenar por
              </label>
              <select
                id="sortBy"
                value={filters.sortBy}
                onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="score">Score</option>
                <option value="budget">Presupuesto</option>
                <option value="published_date">Fecha publicación</option>
              </select>
            </div>

            <div>
              <label htmlFor="sortOrder" className="block text-sm font-medium text-gray-700 mb-1">
                Orden
              </label>
              <select
                id="sortOrder"
                value={filters.sortOrder}
                onChange={(e) => handleFilterChange('sortOrder', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="desc">Descendente</option>
                <option value="asc">Ascendente</option>
              </select>
            </div>
          </div>
        </div>

        {/* Tabla de licitaciones */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            Error al cargar licitaciones: {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Cargando licitaciones...</p>
          </div>
        ) : (
          <>
            <TenderTable tenders={tenders} />
            
            {/* Paginación */}
            {pagination.total > 0 && (
              <div className="mt-6 flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Mostrando {((pagination.page - 1) * pagination.pageSize) + 1} a{' '}
                  {Math.min(pagination.page * pagination.pageSize, pagination.total)} de{' '}
                  {pagination.total} licitaciones
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handlePageChange(pagination.page - 1)}
                    disabled={pagination.page === 1}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Anterior
                  </button>
                  <span className="px-4 py-2 text-sm text-gray-700">
                    Página {pagination.page} de {Math.ceil(pagination.total / pagination.pageSize)}
                  </span>
                  <button
                    onClick={() => handlePageChange(pagination.page + 1)}
                    disabled={pagination.page >= Math.ceil(pagination.total / pagination.pageSize)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Siguiente
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default App
