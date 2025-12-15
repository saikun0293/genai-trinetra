import { useState, useEffect, useMemo } from "react"
import { RefreshCw, BarChart3, X, Filter, FilterX } from "lucide-react"
import { SideNav } from "@/components/SideNav"
import { VerifyView } from "@/components/VerifyView"
import { agentService } from "@/services/agentService"
import ReactMarkdown from "react-markdown"

interface Transaction {
  transaction_id: string
  approval_status: string
  amount?: number
  currency?: string
  payee_country?: string
  vendor_country?: string
  payment_method?: string
  payment_purpose?: string
  payment_time?: string
}

interface TransactionsResponse {
  success: boolean
  count: number
  total: number
  transactions: Transaction[]
}

interface Filters {
  search: string
  status: string
  payeeCountry: string
  vendorCountry: string
  paymentMethod: string
  minAmount: string
  maxAmount: string
}

interface AnalysisData {
  transaction_id: string
  payee_analysis: string | null
  payer_analysis: string | null
  geopolitical_analysis: string | null
  transaction_analysis: string | null
  critic_analysis: string | null
}

type TabType = "conclusion" | "payee" | "payer" | "geopolitics" | "transactions"

export default function App() {
  const [activeView, setActiveView] = useState<"dashboard" | "verify">(
    "dashboard"
  )
  const [allTransactions, setAllTransactions] = useState<Transaction[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [rowsPerPage, setRowsPerPage] = useState<number>(25)
  const [selectedTransaction, setSelectedTransaction] =
    useState<Transaction | null>(null)
  const [activeTab, setActiveTab] = useState<TabType>("conclusion")
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null)
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState<Filters>({
    search: "",
    status: "",
    payeeCountry: "",
    vendorCountry: "",
    paymentMethod: "",
    minAmount: "",
    maxAmount: ""
  })

  useEffect(() => {
    fetchTransactions()
  }, [])

  useEffect(() => {
    const fetchAnalysis = async () => {
      if (selectedTransaction) {
        setIsLoadingAnalysis(true)
        try {
          const analysis = await agentService.getTransactionAnalysis(
            selectedTransaction.transaction_id
          )
          setAnalysisData(analysis)
        } catch (error) {
          console.error("Error fetching analysis:", error)
          setAnalysisData(null)
        } finally {
          setIsLoadingAnalysis(false)
        }
      } else {
        setAnalysisData(null)
      }
    }

    fetchAnalysis()
  }, [selectedTransaction])

  const fetchTransactions = async () => {
    try {
      setIsLoading(true)
      setIsRefreshing(true)
      setError(null)

      const response = await fetch(`/api/getTransactions?fetch_all=true`)

      if (!response.ok) {
        throw new Error(`Failed to fetch transactions: ${response.status}`)
      }

      const data: TransactionsResponse = await response.json()
      setAllTransactions(data.transactions || [])
      setCurrentPage(1) // Reset to first page on refresh
    } catch (err) {
      console.error("Error fetching transactions:", err)
      setError(
        err instanceof Error ? err.message : "Failed to fetch transactions"
      )
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }

  const updateTransactionStatus = async (
    transactionId: string,
    newStatus: string
  ) => {
    try {
      const response = await fetch(`/api/updateTransactionStatus`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          transaction_id: transactionId,
          approval_status: newStatus
        })
      })

      if (!response.ok) {
        throw new Error("Failed to update transaction status")
      }

      // Update local state
      setAllTransactions((prev) =>
        prev.map((t) =>
          t.transaction_id === transactionId
            ? { ...t, approval_status: newStatus }
            : t
        )
      )

      // Update selected transaction if it's the one being updated
      if (selectedTransaction?.transaction_id === transactionId) {
        setSelectedTransaction((prev) =>
          prev ? { ...prev, approval_status: newStatus } : null
        )
      }

      alert(`Transaction ${newStatus} successfully!`)
    } catch (err) {
      console.error("Error updating transaction:", err)
      alert("Failed to update transaction status")
    }
  }

  // Frontend pagination
  const totalCount = allTransactions.length

  // Get unique values for filter dropdowns
  const uniqueStatuses = useMemo(
    () =>
      Array.from(
        new Set(allTransactions.map((t) => t.approval_status).filter(Boolean))
      ),
    [allTransactions]
  )
  const uniquePayeeCountries = useMemo(
    () =>
      Array.from(
        new Set(allTransactions.map((t) => t.payee_country).filter(Boolean))
      ),
    [allTransactions]
  )
  const uniqueVendorCountries = useMemo(
    () =>
      Array.from(
        new Set(allTransactions.map((t) => t.vendor_country).filter(Boolean))
      ),
    [allTransactions]
  )
  const uniquePaymentMethods = useMemo(
    () =>
      Array.from(
        new Set(allTransactions.map((t) => t.payment_method).filter(Boolean))
      ),
    [allTransactions]
  )

  // Apply filters
  const filteredTransactions = useMemo(() => {
    return allTransactions.filter((transaction) => {
      // Search filter
      if (
        filters.search &&
        !transaction.transaction_id
          .toLowerCase()
          .includes(filters.search.toLowerCase())
      ) {
        return false
      }

      // Status filter
      if (filters.status && transaction.approval_status !== filters.status) {
        return false
      }

      // Payee country filter
      if (
        filters.payeeCountry &&
        transaction.payee_country !== filters.payeeCountry
      ) {
        return false
      }

      // Vendor country filter
      if (
        filters.vendorCountry &&
        transaction.vendor_country !== filters.vendorCountry
      ) {
        return false
      }

      // Payment method filter
      if (
        filters.paymentMethod &&
        transaction.payment_method !== filters.paymentMethod
      ) {
        return false
      }

      // Amount filters
      if (
        filters.minAmount &&
        transaction.amount &&
        transaction.amount < Number(filters.minAmount)
      ) {
        return false
      }
      if (
        filters.maxAmount &&
        transaction.amount &&
        transaction.amount > Number(filters.maxAmount)
      ) {
        return false
      }

      return true
    })
  }, [allTransactions, filters])

  // Update pagination based on filtered results
  const filteredTotalCount = filteredTransactions.length
  const filteredStartIndex = (currentPage - 1) * rowsPerPage
  const filteredEndIndex = filteredStartIndex + rowsPerPage
  const filteredPaginatedTransactions = filteredTransactions.slice(
    filteredStartIndex,
    filteredEndIndex
  )
  const filteredTotalPages = Math.ceil(filteredTotalCount / rowsPerPage)

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [filters])

  const resetFilters = () => {
    setFilters({
      search: "",
      status: "",
      payeeCountry: "",
      vendorCountry: "",
      paymentMethod: "",
      minAmount: "",
      maxAmount: ""
    })
  }

  const activeFilterCount = useMemo(() => {
    return Object.values(filters).filter((value) => value !== "").length
  }, [filters])

  const PaginationControls = () => (
    <div
      className="flex items-center justify-between rounded-lg px-6 py-4"
      style={{ backgroundColor: "#1E1F20", border: "1px solid #2D2E2F" }}
    >
      <div className="flex items-center gap-4">
        <span className="text-sm" style={{ color: "#B8BCC1" }}>
          Showing {filteredStartIndex + 1} to{" "}
          {Math.min(filteredEndIndex, filteredTotalCount)} of{" "}
          {filteredTotalCount}
          {activeFilterCount > 0 && ` (filtered from ${totalCount})`}
        </span>
        <div className="flex items-center gap-2">
          <label
            htmlFor="rowsPerPage"
            className="text-sm"
            style={{ color: "#B8BCC1" }}
          >
            Rows per page:
          </label>
          <select
            id="rowsPerPage"
            value={rowsPerPage}
            onChange={(e) => {
              setRowsPerPage(Number(e.target.value))
              setCurrentPage(1)
            }}
            className="rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{
              backgroundColor: "#2D2E2F",
              color: "#B8BCC1",
              border: "1px solid #3C3D3F"
            }}
          >
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={() => setCurrentPage(1)}
          disabled={currentPage === 1}
          className="px-3 py-1 text-sm rounded disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:opacity-80"
          style={{ backgroundColor: "#2D2E2F", color: "#B8BCC1" }}
        >
          First
        </button>
        <button
          onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
          disabled={currentPage === 1}
          className="px-3 py-1 text-sm rounded disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:opacity-80"
          style={{ backgroundColor: "#2D2E2F", color: "#B8BCC1" }}
        >
          Previous
        </button>
        <span className="text-sm px-3" style={{ color: "#B8BCC1" }}>
          Page {currentPage} of {filteredTotalPages || 1}
        </span>
        <button
          onClick={() => setCurrentPage((prev) => prev + 1)}
          disabled={currentPage >= filteredTotalPages}
          className="px-3 py-1 text-sm rounded disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:opacity-80"
          style={{ backgroundColor: "#2D2E2F", color: "#B8BCC1" }}
        >
          Next
        </button>
        <button
          onClick={() => setCurrentPage(filteredTotalPages)}
          disabled={currentPage >= filteredTotalPages}
          className="px-3 py-1 text-sm rounded disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:opacity-80"
          style={{ backgroundColor: "#2D2E2F", color: "#B8BCC1" }}
        >
          Last
        </button>
      </div>
    </div>
  )

  const renderTabContent = () => {
    if (!selectedTransaction) return null

    const isInReview =
      selectedTransaction.approval_status.toLowerCase().includes("review") ||
      selectedTransaction.approval_status.toLowerCase() === "in review" ||
      selectedTransaction.approval_status.toLowerCase() === "pending"

    if (isLoadingAnalysis) {
      return (
        <div className="flex items-center justify-center py-12">
          <div className="text-center space-y-4">
            <div className="w-12 h-12 border-4 border-neutral-600 border-t-blue-500 rounded-full animate-spin mx-auto"></div>
            <p className="text-sm" style={{ color: "#B8BCC1" }}>
              Loading analysis...
            </p>
          </div>
        </div>
      )
    }

    switch (activeTab) {
      case "conclusion":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold" style={{ color: "#E8EAED" }}>
              Analysis Conclusion
            </h3>
            {analysisData?.critic_analysis ? (
              <div
                className="prose prose-invert max-w-none"
                style={{ color: "#B8BCC1" }}
              >
                <ReactMarkdown className="text-sm">
                  {analysisData.critic_analysis}
                </ReactMarkdown>
              </div>
            ) : (
              <p style={{ color: "#B8BCC1" }}>
                No analysis available for this transaction. Please run the
                compliance analysis first.
              </p>
            )}
            <div className="p-4 rounded" style={{ backgroundColor: "#2D2E2F" }}>
              <p className="text-sm" style={{ color: "#B8BCC1" }}>
                <strong>Transaction ID:</strong>{" "}
                {selectedTransaction.transaction_id}
              </p>
              <p className="text-sm mt-2" style={{ color: "#B8BCC1" }}>
                <strong>Current Status:</strong>{" "}
                {selectedTransaction.approval_status}
              </p>
            </div>
            {isInReview && (
              <div className="flex gap-3 mt-6">
                <button
                  onClick={() =>
                    updateTransactionStatus(
                      selectedTransaction.transaction_id,
                      "Approved"
                    )
                  }
                  className="flex-1 px-4 py-2 rounded font-medium transition-all hover:opacity-90"
                  style={{ backgroundColor: "#22c55e", color: "#fff" }}
                >
                  Approve Transaction
                </button>
                <button
                  onClick={() =>
                    updateTransactionStatus(
                      selectedTransaction.transaction_id,
                      "Rejected"
                    )
                  }
                  className="flex-1 px-4 py-2 rounded font-medium transition-all hover:opacity-90"
                  style={{ backgroundColor: "#ef4444", color: "#fff" }}
                >
                  Reject Transaction
                </button>
              </div>
            )}
          </div>
        )
      case "payee":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold" style={{ color: "#E8EAED" }}>
              Payee Information
            </h3>
            {analysisData?.payee_analysis ? (
              <div
                className="prose prose-invert max-w-none"
                style={{ color: "#B8BCC1" }}
              >
                <ReactMarkdown className="text-sm">
                  {analysisData.payee_analysis}
                </ReactMarkdown>
              </div>
            ) : (
              <p style={{ color: "#B8BCC1" }}>
                No payee analysis available for this transaction.
              </p>
            )}
            <div className="p-4 rounded" style={{ backgroundColor: "#2D2E2F" }}>
              <p className="text-sm" style={{ color: "#B8BCC1" }}>
                <strong>Country:</strong>{" "}
                {selectedTransaction.payee_country || "N/A"}
              </p>
            </div>
          </div>
        )
      case "payer":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold" style={{ color: "#E8EAED" }}>
              Payer (Vendor) Information
            </h3>
            {analysisData?.payer_analysis ? (
              <div
                className="prose prose-invert max-w-none"
                style={{ color: "#B8BCC1" }}
              >
                <ReactMarkdown className="text-sm">
                  {analysisData.payer_analysis}
                </ReactMarkdown>
              </div>
            ) : (
              <p style={{ color: "#B8BCC1" }}>
                No payer analysis available for this transaction.
              </p>
            )}
            <div className="p-4 rounded" style={{ backgroundColor: "#2D2E2F" }}>
              <p className="text-sm" style={{ color: "#B8BCC1" }}>
                <strong>Country:</strong>{" "}
                {selectedTransaction.vendor_country || "N/A"}
              </p>
            </div>
          </div>
        )
      case "geopolitics":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold" style={{ color: "#E8EAED" }}>
              Geopolitical Analysis
            </h3>
            {analysisData?.geopolitical_analysis ? (
              <div
                className="prose prose-invert max-w-none"
                style={{ color: "#B8BCC1" }}
              >
                <ReactMarkdown className="text-sm">
                  {analysisData.geopolitical_analysis}
                </ReactMarkdown>
              </div>
            ) : (
              <p style={{ color: "#B8BCC1" }}>
                No geopolitical analysis available for this transaction.
              </p>
            )}
            <div className="p-4 rounded" style={{ backgroundColor: "#2D2E2F" }}>
              <p className="text-sm" style={{ color: "#B8BCC1" }}>
                <strong>Route:</strong> {selectedTransaction.payee_country} →{" "}
                {selectedTransaction.vendor_country}
              </p>
            </div>
          </div>
        )
      case "transactions":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold" style={{ color: "#E8EAED" }}>
              Transaction Analysis
            </h3>
            {analysisData?.transaction_analysis ? (
              <div
                className="prose prose-invert max-w-none"
                style={{ color: "#B8BCC1" }}
              >
                <ReactMarkdown className="text-sm">
                  {analysisData.transaction_analysis}
                </ReactMarkdown>
              </div>
            ) : (
              <p style={{ color: "#B8BCC1" }}>
                No transaction analysis available.
              </p>
            )}
          </div>
        )
    }
  }

  const getRowColor = (status: string) => {
    const normalizedStatus = status?.toLowerCase() || ""

    if (
      normalizedStatus.includes("approved") ||
      normalizedStatus === "approved"
    ) {
      return { backgroundColor: "#1A2E1A", borderBottom: "1px solid #2D2E2F" }
    } else if (
      normalizedStatus.includes("review") ||
      normalizedStatus === "in review" ||
      normalizedStatus === "pending"
    ) {
      return { backgroundColor: "#2E2A1A", borderBottom: "1px solid #2D2E2F" }
    } else {
      return { backgroundColor: "#2E1A1A", borderBottom: "1px solid #2D2E2F" }
    }
  }

  const getStatusBadgeColor = (status: string) => {
    const normalizedStatus = status?.toLowerCase() || ""

    if (
      normalizedStatus.includes("approved") ||
      normalizedStatus === "approved"
    ) {
      return "bg-green-100 text-green-800 border-green-300"
    } else if (
      normalizedStatus.includes("review") ||
      normalizedStatus === "in review" ||
      normalizedStatus === "pending"
    ) {
      return "bg-yellow-100 text-yellow-800 border-yellow-300"
    } else {
      return "bg-red-100 text-red-800 border-red-300"
    }
  }

  if (isLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: "#0F1011" }}
      >
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-neutral-600 border-t-blue-500 rounded-full animate-spin mx-auto"></div>
          <p className="text-xl" style={{ color: "#B8BCC1" }}>
            Loading transactions...
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: "#0F1011" }}
      >
        <div className="text-center space-y-4">
          <p className="text-xl text-red-400">Error: {error}</p>
          <button
            onClick={fetchTransactions}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex" style={{ backgroundColor: "#0F1011" }}>
      {/* Side Navigation */}
      <SideNav activeView={activeView} onViewChange={setActiveView} />

      {/* Main Content Area */}
      <div className="flex-1 ml-20">
        {activeView === "verify" ? (
          <VerifyView />
        ) : (
          <div className="p-6 flex">
            <div
              className={`transition-all duration-300 ${
                selectedTransaction ? "mr-[500px]" : "mr-0"
              } flex-1`}
            >
              <div className="max-w-7xl mx-auto">
                <div className="mb-6">
                  <h1 className="text-5xl font-bold mb-3 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                    Payment Compliance Dashboard
                  </h1>
                  <div className="flex items-center justify-between">
                    <div
                      className="flex items-center gap-4"
                      style={{ color: "#B8BCC1" }}
                    >
                      <p>
                        Total:{" "}
                        <span
                          className="font-semibold"
                          style={{ color: "#E8EAED" }}
                        >
                          {totalCount}
                        </span>{" "}
                        transactions
                      </p>
                      {activeFilterCount > 0 && (
                        <p>
                          Filtered:{" "}
                          <span
                            className="font-semibold"
                            style={{ color: "#60A5FA" }}
                          >
                            {filteredTotalCount}
                          </span>
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setShowFilters(!showFilters)}
                        className="flex items-center gap-2 px-4 py-2 rounded transition-all hover:opacity-80"
                        style={{ backgroundColor: "#2D2E2F", color: "#B8BCC1" }}
                      >
                        <Filter className="w-4 h-4" />
                        Filters
                        {activeFilterCount > 0 && (
                          <span
                            className="px-2 py-0.5 text-xs rounded-full"
                            style={{
                              backgroundColor: "#60A5FA",
                              color: "#fff"
                            }}
                          >
                            {activeFilterCount}
                          </span>
                        )}
                      </button>
                      <button
                        onClick={fetchTransactions}
                        disabled={isRefreshing}
                        className="flex items-center gap-2 px-4 py-2 rounded transition-all hover:opacity-80 disabled:opacity-50"
                        style={{ backgroundColor: "#2D2E2F", color: "#B8BCC1" }}
                      >
                        <RefreshCw
                          className={`w-4 h-4 ${
                            isRefreshing ? "animate-spin" : ""
                          }`}
                        />
                        Refresh Data
                      </button>
                    </div>
                  </div>
                </div>

                {/* Filter Panel */}
                {showFilters && (
                  <div
                    className="mb-4 p-6 rounded-lg"
                    style={{
                      backgroundColor: "#1E1F20",
                      border: "1px solid #2D2E2F"
                    }}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3
                        className="text-lg font-semibold"
                        style={{ color: "#E8EAED" }}
                      >
                        Filter Transactions
                      </h3>
                      <button
                        onClick={resetFilters}
                        className="flex items-center gap-2 px-3 py-1 text-sm rounded transition-all hover:opacity-80"
                        style={{ backgroundColor: "#2D2E2F", color: "#B8BCC1" }}
                        disabled={activeFilterCount === 0}
                      >
                        <FilterX className="w-4 h-4" />
                        Reset Filters
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {/* Search */}
                      <div>
                        <label
                          className="block text-sm mb-2"
                          style={{ color: "#B8BCC1" }}
                        >
                          Search Transaction ID
                        </label>
                        <input
                          type="text"
                          value={filters.search}
                          onChange={(e) =>
                            setFilters({ ...filters, search: e.target.value })
                          }
                          placeholder="Enter transaction ID..."
                          className="w-full px-3 py-2 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          style={{
                            backgroundColor: "#2D2E2F",
                            color: "#B8BCC1",
                            border: "1px solid #3C3D3F"
                          }}
                        />
                      </div>

                      {/* Status */}
                      <div>
                        <label
                          className="block text-sm mb-2"
                          style={{ color: "#B8BCC1" }}
                        >
                          Status
                        </label>
                        <select
                          value={filters.status}
                          onChange={(e) =>
                            setFilters({ ...filters, status: e.target.value })
                          }
                          className="w-full px-3 py-2 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          style={{
                            backgroundColor: "#2D2E2F",
                            color: "#B8BCC1",
                            border: "1px solid #3C3D3F"
                          }}
                        >
                          <option value="">All Statuses</option>
                          {uniqueStatuses.map((status) => (
                            <option key={status} value={status}>
                              {status}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Payee Country */}
                      <div>
                        <label
                          className="block text-sm mb-2"
                          style={{ color: "#B8BCC1" }}
                        >
                          Payee Country (From)
                        </label>
                        <select
                          value={filters.payeeCountry}
                          onChange={(e) =>
                            setFilters({
                              ...filters,
                              payeeCountry: e.target.value
                            })
                          }
                          className="w-full px-3 py-2 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          style={{
                            backgroundColor: "#2D2E2F",
                            color: "#B8BCC1",
                            border: "1px solid #3C3D3F"
                          }}
                        >
                          <option value="">All Countries</option>
                          {uniquePayeeCountries.sort().map((country) => (
                            <option key={country} value={country}>
                              {country}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Vendor Country */}
                      <div>
                        <label
                          className="block text-sm mb-2"
                          style={{ color: "#B8BCC1" }}
                        >
                          Vendor Country (To)
                        </label>
                        <select
                          value={filters.vendorCountry}
                          onChange={(e) =>
                            setFilters({
                              ...filters,
                              vendorCountry: e.target.value
                            })
                          }
                          className="w-full px-3 py-2 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          style={{
                            backgroundColor: "#2D2E2F",
                            color: "#B8BCC1",
                            border: "1px solid #3C3D3F"
                          }}
                        >
                          <option value="">All Countries</option>
                          {uniqueVendorCountries.sort().map((country) => (
                            <option key={country} value={country}>
                              {country}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Payment Method */}
                      <div>
                        <label
                          className="block text-sm mb-2"
                          style={{ color: "#B8BCC1" }}
                        >
                          Payment Method
                        </label>
                        <select
                          value={filters.paymentMethod}
                          onChange={(e) =>
                            setFilters({
                              ...filters,
                              paymentMethod: e.target.value
                            })
                          }
                          className="w-full px-3 py-2 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          style={{
                            backgroundColor: "#2D2E2F",
                            color: "#B8BCC1",
                            border: "1px solid #3C3D3F"
                          }}
                        >
                          <option value="">All Methods</option>
                          {uniquePaymentMethods.sort().map((method) => (
                            <option key={method} value={method}>
                              {method}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Min Amount */}
                      <div>
                        <label
                          className="block text-sm mb-2"
                          style={{ color: "#B8BCC1" }}
                        >
                          Min Amount
                        </label>
                        <input
                          type="number"
                          value={filters.minAmount}
                          onChange={(e) =>
                            setFilters({
                              ...filters,
                              minAmount: e.target.value
                            })
                          }
                          placeholder="0"
                          className="w-full px-3 py-2 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          style={{
                            backgroundColor: "#2D2E2F",
                            color: "#B8BCC1",
                            border: "1px solid #3C3D3F"
                          }}
                        />
                      </div>

                      {/* Max Amount */}
                      <div>
                        <label
                          className="block text-sm mb-2"
                          style={{ color: "#B8BCC1" }}
                        >
                          Max Amount
                        </label>
                        <input
                          type="number"
                          value={filters.maxAmount}
                          onChange={(e) =>
                            setFilters({
                              ...filters,
                              maxAmount: e.target.value
                            })
                          }
                          placeholder="999999999"
                          className="w-full px-3 py-2 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          style={{
                            backgroundColor: "#2D2E2F",
                            color: "#B8BCC1",
                            border: "1px solid #3C3D3F"
                          }}
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* Top Pagination */}
                {filteredTotalCount > 0 && (
                  <div className="mb-4">
                    <PaginationControls />
                  </div>
                )}

                <div
                  className="rounded-lg shadow-2xl overflow-hidden"
                  style={{
                    backgroundColor: "#1E1F20",
                    border: "1px solid #2D2E2F"
                  }}
                >
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead style={{ backgroundColor: "#17181A" }}>
                        <tr>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#B8BCC1" }}
                          >
                            Transaction ID
                          </th>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#B8BCC1" }}
                          >
                            Status
                          </th>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#B8BCC1" }}
                          >
                            Amount
                          </th>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#B8BCC1" }}
                          >
                            Payment Method
                          </th>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#B8BCC1" }}
                          >
                            Countries
                          </th>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#B8BCC1" }}
                          >
                            Purpose
                          </th>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#B8BCC1" }}
                          >
                            Payment Time
                          </th>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#B8BCC1" }}
                          >
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody style={{ borderTop: "1px solid #2D2E2F" }}>
                        {filteredPaginatedTransactions.map((transaction) => (
                          <tr
                            key={transaction.transaction_id}
                            className="transition-colors hover:opacity-80"
                            style={getRowColor(transaction.approval_status)}
                          >
                            <td
                              className="px-6 py-4 whitespace-nowrap text-sm font-medium"
                              style={{ color: "#B8BCC1" }}
                            >
                              {transaction.transaction_id}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span
                                className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getStatusBadgeColor(
                                  transaction.approval_status
                                )}`}
                              >
                                {transaction.approval_status}
                              </span>
                            </td>
                            <td
                              className="px-6 py-4 whitespace-nowrap text-sm"
                              style={{ color: "#B8BCC1" }}
                            >
                              {transaction.amount
                                ? `${
                                    transaction.currency || ""
                                  } ${transaction.amount.toLocaleString()}`
                                : "N/A"}
                            </td>
                            <td
                              className="px-6 py-4 whitespace-nowrap text-sm"
                              style={{ color: "#B8BCC1" }}
                            >
                              {transaction.payment_method || "N/A"}
                            </td>
                            <td
                              className="px-6 py-4 text-sm"
                              style={{ color: "#B8BCC1" }}
                            >
                              <div className="flex flex-col">
                                <span>
                                  From: {transaction.payee_country || "N/A"}
                                </span>
                                <span>
                                  To: {transaction.vendor_country || "N/A"}
                                </span>
                              </div>
                            </td>
                            <td
                              className="px-6 py-4 text-sm"
                              style={{ color: "#B8BCC1" }}
                            >
                              {transaction.payment_purpose || "N/A"}
                            </td>
                            <td
                              className="px-6 py-4 whitespace-nowrap text-sm"
                              style={{ color: "#B8BCC1" }}
                            >
                              {transaction.payment_time || "N/A"}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              <button
                                onClick={() => {
                                  setSelectedTransaction(transaction)
                                  setActiveTab("conclusion")
                                }}
                                className="p-2 rounded transition-all hover:opacity-80"
                                style={{
                                  backgroundColor: "#2D2E2F",
                                  color: "#B8BCC1"
                                }}
                                title="Analyze Transaction"
                              >
                                <BarChart3 className="w-4 h-4" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {filteredPaginatedTransactions.length === 0 && !isLoading && (
                  <div className="text-center mt-8">
                    <p style={{ color: "#B8BCC1" }}>
                      {activeFilterCount > 0
                        ? "No transactions match the current filters"
                        : "No transactions found"}
                    </p>
                    {activeFilterCount > 0 && (
                      <button
                        onClick={resetFilters}
                        className="mt-4 px-4 py-2 rounded transition-all hover:opacity-80"
                        style={{ backgroundColor: "#2D2E2F", color: "#B8BCC1" }}
                      >
                        Clear Filters
                      </button>
                    )}
                  </div>
                )}

                {/* Bottom Pagination */}
                {filteredTotalCount > 0 && (
                  <div className="mt-6">
                    <PaginationControls />
                  </div>
                )}
              </div>
            </div>

            {/* Side Panel */}
            {selectedTransaction && (
              <div
                className="fixed right-0 top-0 h-full w-[500px] shadow-2xl overflow-y-auto"
                style={{
                  backgroundColor: "#1E1F20",
                  borderLeft: "1px solid #2D2E2F"
                }}
              >
                <div
                  className="sticky top-0 z-10 flex items-center justify-between p-6"
                  style={{
                    backgroundColor: "#17181A",
                    borderBottom: "1px solid #2D2E2F"
                  }}
                >
                  <h2
                    className="text-xl font-bold"
                    style={{ color: "#E8EAED" }}
                  >
                    Transaction Analysis
                  </h2>
                  <button
                    onClick={() => setSelectedTransaction(null)}
                    className="p-2 rounded transition-all hover:opacity-80"
                    style={{ backgroundColor: "#2D2E2F", color: "#B8BCC1" }}
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Tabs */}
                <div
                  className="flex border-b"
                  style={{ borderColor: "#2D2E2F", backgroundColor: "#17181A" }}
                >
                  {[
                    { id: "conclusion", label: "Conclusion" },
                    { id: "payee", label: "Payee" },
                    { id: "payer", label: "Payer" },
                    { id: "geopolitics", label: "Geopolitics" },
                    { id: "transactions", label: "History" }
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as TabType)}
                      className="flex-1 px-4 py-3 text-sm font-medium transition-all"
                      style={{
                        color: activeTab === tab.id ? "#60A5FA" : "#B8BCC1",
                        borderBottom:
                          activeTab === tab.id
                            ? "2px solid #60A5FA"
                            : "2px solid transparent"
                      }}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* Tab Content */}
                <div className="p-6">{renderTabContent()}</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
