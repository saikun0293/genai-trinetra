import { useState, useEffect, useMemo } from "react"
import { RefreshCw, BarChart3, X, Filter, FilterX } from "lucide-react"
import { SideNav } from "@/components/SideNav"
import { VerifyView, ChatMessage } from "@/components/VerifyView"
import { agentService } from "@/services/agentService"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

// Utility function to strip markdown/json code blocks
const stripCodeBlocks = (content: string | null): string | null => {
  if (!content) return content

  // Remove markdown code blocks: ```markdown ... ```, ```json ... ```, etc.
  const codeBlockPattern = /^```(?:json|markdown|md)?\s*\n?([\s\S]*?)\n?```$/
  const match = content.trim().match(codeBlockPattern)

  if (match) {
    return match[1].trim()
  }

  return content
}

interface Transaction {
  transaction_id: string
  approval_status: string
  payment_amount?: number
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
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
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
          ?.toLowerCase()
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
        transaction.payment_amount &&
        transaction.payment_amount < Number(filters.minAmount)
      ) {
        return false
      }
      if (
        filters.maxAmount &&
        transaction.payment_amount &&
        transaction.payment_amount > Number(filters.maxAmount)
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
      style={{ backgroundColor: "#FFFFFF", border: "1px solid #D0D5DD" }}
    >
      <div className="flex items-center gap-4">
        <span className="text-sm" style={{ color: "#3B4953" }}>
          Showing {filteredStartIndex + 1} to{" "}
          {Math.min(filteredEndIndex, filteredTotalCount)} of{" "}
          {filteredTotalCount}
          {activeFilterCount > 0 && ` (filtered from ${totalCount})`}
        </span>
        <div className="flex items-center gap-2">
          <label
            htmlFor="rowsPerPage"
            className="text-sm"
            style={{ color: "#3B4953" }}
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
              backgroundColor: "#F0F4F8",
              color: "#000000",
              border: "1px solid #D0D5DD"
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
          style={{ backgroundColor: "#E9EEF6", color: "#3B4953" }}
        >
          First
        </button>
        <button
          onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
          disabled={currentPage === 1}
          className="px-3 py-1 text-sm rounded disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:opacity-80"
          style={{ backgroundColor: "#E9EEF6", color: "#3B4953" }}
        >
          Previous
        </button>
        <span className="text-sm px-3" style={{ color: "#3B4953" }}>
          Page {currentPage} of {filteredTotalPages || 1}
        </span>
        <button
          onClick={() => setCurrentPage((prev) => prev + 1)}
          disabled={currentPage >= filteredTotalPages}
          className="px-3 py-1 text-sm rounded disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:opacity-80"
          style={{ backgroundColor: "#E9EEF6", color: "#3B4953" }}
        >
          Next
        </button>
        <button
          onClick={() => setCurrentPage(filteredTotalPages)}
          disabled={currentPage >= filteredTotalPages}
          className="px-3 py-1 text-sm rounded disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:opacity-80"
          style={{ backgroundColor: "#E9EEF6", color: "#3B4953" }}
        >
          Last
        </button>
      </div>
    </div>
  )

  const renderTabContent = () => {
    if (!selectedTransaction) return null

    if (isLoadingAnalysis) {
      return (
        <div className="flex items-center justify-center py-12">
          <div className="text-center space-y-4">
            <div className="w-12 h-12 border-4 border-neutral-300 border-t-blue-500 rounded-full animate-spin mx-auto"></div>
            <p className="text-sm" style={{ color: "#3B4953" }}>
              Loading analysis...
            </p>
          </div>
        </div>
      )
    }

    switch (activeTab) {
      case "conclusion": {
        interface CriticData {
          final_decision?: {
            score: number
            confidence_score: number
            category: string
            reason: string
            notes?: string
          }
          critique_agent_response_markdown?: string
        }

        let criticData: CriticData | null = null
        try {
          if (analysisData?.critic_analysis) {
            // Strip code blocks before parsing JSON
            const cleanedJson = stripCodeBlocks(analysisData.critic_analysis)
            if (cleanedJson) {
              criticData = JSON.parse(cleanedJson)
            }
          }
        } catch (e) {
          console.error("Failed to parse critic_analysis JSON:", e)
          console.error("Raw data:", analysisData?.critic_analysis)
        }

        const finalDecision = criticData?.final_decision
        const markdown = criticData?.critique_agent_response_markdown

        const getCategoryColor = (category: string) => {
          switch (category) {
            case "APPROVED":
              return "#22c55e"
            case "REJECTED":
              return "#ef4444"
            case "REVIEW":
              return "#f59e0b"
            default:
              return "#6b7280"
          }
        }

        const getCategoryBg = (category: string) => {
          switch (category) {
            case "APPROVED":
              return "#E6F4EA"
            case "REJECTED":
              return "#FCE8E8"
            case "REVIEW":
              return "#FEF7E0"
            default:
              return "#E9EEF6"
          }
        }

        return (
          <div className="space-y-6">
            {analysisData?.critic_analysis ? (
              <>
                {/* Final Decision Section */}
                {finalDecision && (
                  <div
                    className="rounded-lg p-6 space-y-4"
                    style={{
                      backgroundColor: getCategoryBg(finalDecision.category)
                    }}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3
                        className="text-xl font-bold"
                        style={{ color: "#000000" }}
                      >
                        Final Decision
                      </h3>
                      <span
                        className="px-4 py-2 rounded-full font-bold text-sm"
                        style={{
                          backgroundColor: getCategoryColor(
                            finalDecision.category
                          ),
                          color: "#fff"
                        }}
                      >
                        {finalDecision.category}
                      </span>
                    </div>

                    {/* Score Meters */}
                    <div className="grid grid-cols-2 gap-4">
                      {/* Risk Score */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span
                            className="text-sm font-medium"
                            style={{ color: "#3B4953" }}
                          >
                            Risk Score
                          </span>
                          <span
                            className="text-lg font-bold"
                            style={{ color: "#000000" }}
                          >
                            {finalDecision.score}/100
                          </span>
                        </div>
                        <div
                          className="h-3 rounded-full overflow-hidden"
                          style={{ backgroundColor: "#E9EEF6" }}
                        >
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{
                              width: `${finalDecision.score}%`,
                              backgroundColor:
                                finalDecision.score < 30
                                  ? "#22c55e"
                                  : finalDecision.score < 70
                                  ? "#f59e0b"
                                  : "#ef4444"
                            }}
                          />
                        </div>
                      </div>

                      {/* Confidence Score */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span
                            className="text-sm font-medium"
                            style={{ color: "#3B4953" }}
                          >
                            Confidence
                          </span>
                          <span
                            className="text-lg font-bold"
                            style={{ color: "#000000" }}
                          >
                            {finalDecision.confidence_score}/100
                          </span>
                        </div>
                        <div
                          className="h-3 rounded-full overflow-hidden"
                          style={{ backgroundColor: "#E9EEF6" }}
                        >
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{
                              width: `${finalDecision.confidence_score}%`,
                              backgroundColor: "#60A5FA"
                            }}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Reason */}
                    <div className="space-y-2">
                      <h4
                        className="text-sm font-semibold"
                        style={{ color: "#000000" }}
                      >
                        Reason
                      </h4>
                      <p className="text-sm" style={{ color: "#3B4953" }}>
                        {finalDecision.reason}
                      </p>
                    </div>

                    {/* Notes */}
                    {finalDecision.notes && (
                      <div className="space-y-2">
                        <h4
                          className="text-sm font-semibold"
                          style={{ color: "#000000" }}
                        >
                          Additional Notes
                        </h4>
                        <p className="text-sm" style={{ color: "#3B4953" }}>
                          {finalDecision.notes}
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* Markdown Analysis */}
                {markdown && (
                  <div
                    className="max-w-none markdown-analysis"
                    style={{ color: "#3B4953" }}
                  >
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {stripCodeBlocks(markdown) || markdown}
                    </ReactMarkdown>
                  </div>
                )}

                {/* Transaction Info */}
                <div
                  className="p-4 rounded"
                  style={{ backgroundColor: "#E9EEF6" }}
                >
                  <p className="text-sm" style={{ color: "#3B4953" }}>
                    <strong>Transaction ID:</strong>{" "}
                    {selectedTransaction.transaction_id}
                  </p>
                  <p className="text-sm mt-2" style={{ color: "#3B4953" }}>
                    <strong>Current Status:</strong>{" "}
                    {selectedTransaction.approval_status}
                  </p>
                </div>
              </>
            ) : (
              <p style={{ color: "#3B4953" }}>
                No analysis available for this transaction. Please run the
                compliance analysis first.
              </p>
            )}
          </div>
        )
      }
      case "payee":
        return (
          <div className="space-y-4">
            {analysisData?.payee_analysis ? (
              <div
                className="max-w-none markdown-analysis"
                style={{ color: "#3B4953" }}
              >
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {stripCodeBlocks(analysisData.payee_analysis) ||
                    analysisData.payee_analysis}
                </ReactMarkdown>
              </div>
            ) : (
              <p style={{ color: "#3B4953" }}>
                No payee analysis available for this transaction.
              </p>
            )}
            <div className="p-4 rounded" style={{ backgroundColor: "#E9EEF6" }}>
              <p className="text-sm" style={{ color: "#3B4953" }}>
                <strong>Country:</strong>{" "}
                {selectedTransaction.payee_country || "N/A"}
              </p>
            </div>
          </div>
        )
      case "payer":
        return (
          <div className="space-y-4">
            {analysisData?.payer_analysis ? (
              <div
                className="max-w-none markdown-analysis"
                style={{ color: "#3B4953" }}
              >
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {stripCodeBlocks(analysisData.payer_analysis) ||
                    analysisData.payer_analysis}
                </ReactMarkdown>
              </div>
            ) : (
              <p style={{ color: "#3B4953" }}>
                No payer analysis available for this transaction.
              </p>
            )}
            <div className="p-4 rounded" style={{ backgroundColor: "#E9EEF6" }}>
              <p className="text-sm" style={{ color: "#3B4953" }}>
                <strong>Country:</strong>{" "}
                {selectedTransaction.vendor_country || "N/A"}
              </p>
            </div>
          </div>
        )
      case "geopolitics":
        return (
          <div className="space-y-4">
            {analysisData?.geopolitical_analysis ? (
              <div
                className="max-w-none markdown-analysis"
                style={{ color: "#3B4953" }}
              >
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {stripCodeBlocks(analysisData.geopolitical_analysis) ||
                    analysisData.geopolitical_analysis}
                </ReactMarkdown>
              </div>
            ) : (
              <p style={{ color: "#3B4953" }}>
                No geopolitical analysis available for this transaction.
              </p>
            )}
            <div className="p-4 rounded" style={{ backgroundColor: "#E9EEF6" }}>
              <p className="text-sm" style={{ color: "#3B4953" }}>
                <strong>Route:</strong> {selectedTransaction.payee_country} →{" "}
                {selectedTransaction.vendor_country}
              </p>
            </div>
          </div>
        )
      case "transactions":
        return (
          <div className="space-y-4">
            {analysisData?.transaction_analysis ? (
              <div
                className="max-w-none markdown-analysis"
                style={{ color: "#3B4953" }}
              >
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {stripCodeBlocks(analysisData.transaction_analysis) ||
                    analysisData.transaction_analysis}
                </ReactMarkdown>
              </div>
            ) : (
              <p style={{ color: "#3B4953" }}>
                No transaction analysis available.
              </p>
            )}
          </div>
        )
    }
  }

  const getRowColor = () => {
    return { backgroundColor: "#FFFFFF", borderBottom: "1px solid #D0D5DD" }
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
        style={{ backgroundColor: "#F0F4F8" }}
      >
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-neutral-300 border-t-blue-500 rounded-full animate-spin mx-auto"></div>
          <p className="text-xl" style={{ color: "#3B4953" }}>
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
        style={{ backgroundColor: "#F0F4F8" }}
      >
        <div className="text-center space-y-4">
          <p className="text-xl text-red-600">Error: {error}</p>
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
    <div className="min-h-screen flex" style={{ backgroundColor: "#F0F4F8" }}>
      {/* Side Navigation */}
      <SideNav activeView={activeView} onViewChange={setActiveView} />

      {/* Main Content Area */}
      <div className="flex-1 ml-20">
        {activeView === "verify" ? (
          <VerifyView
            messages={chatMessages}
            setMessages={setChatMessages}
            onAnalysisComplete={fetchTransactions}
          />
        ) : (
          <div className="p-8 flex">
            <div
              className={`transition-all duration-300 ${
                selectedTransaction ? "mr-[500px]" : "mr-0"
              } flex-1`}
            >
              <div className="max-w-7xl mx-auto">
                <div className="my-8 px-4">
                  <h1
                    className="font-bold mb-4 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent"
                    style={{ fontSize: "2.5rem" }}
                  >
                    Payment Compliance Dashboard
                  </h1>
                  <div className="flex items-center justify-between">
                    <div
                      className="flex items-center gap-4"
                      style={{ color: "#3B4953" }}
                    >
                      <p>
                        Total:{" "}
                        <span
                          className="font-semibold"
                          style={{ color: "#000000" }}
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
                            style={{ color: "#3b82f6" }}
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
                        style={{ backgroundColor: "#E9EEF6", color: "#3B4953" }}
                      >
                        <Filter className="w-4 h-4" />
                        Filters
                        {activeFilterCount > 0 && (
                          <span
                            className="px-2 py-0.5 text-xs rounded-full"
                            style={{
                              backgroundColor: "#3b82f6",
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
                        style={{ backgroundColor: "#E9EEF6", color: "#3B4953" }}
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
                      backgroundColor: "#FFFFFF",
                      border: "1px solid #D0D5DD"
                    }}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3
                        className="text-lg font-semibold"
                        style={{ color: "#000000" }}
                      >
                        Filter Transactions
                      </h3>
                      <button
                        onClick={resetFilters}
                        className="flex items-center gap-2 px-3 py-1 text-sm rounded transition-all hover:opacity-80"
                        style={{ backgroundColor: "#E9EEF6", color: "#3B4953" }}
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
                          style={{ color: "#3B4953" }}
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
                            backgroundColor: "#F0F4F8",
                            color: "#000000",
                            border: "1px solid #D0D5DD"
                          }}
                        />
                      </div>

                      {/* Status */}
                      <div>
                        <label
                          className="block text-sm mb-2"
                          style={{ color: "#3B4953" }}
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
                            backgroundColor: "#F0F4F8",
                            color: "#000000",
                            border: "1px solid #D0D5DD"
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
                          style={{ color: "#3B4953" }}
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
                            backgroundColor: "#F0F4F8",
                            color: "#000000",
                            border: "1px solid #D0D5DD"
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
                          style={{ color: "#3B4953" }}
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
                            backgroundColor: "#F0F4F8",
                            color: "#000000",
                            border: "1px solid #D0D5DD"
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
                          style={{ color: "#3B4953" }}
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
                            backgroundColor: "#F0F4F8",
                            color: "#000000",
                            border: "1px solid #D0D5DD"
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
                          style={{ color: "#3B4953" }}
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
                            backgroundColor: "#F0F4F8",
                            color: "#000000",
                            border: "1px solid #D0D5DD"
                          }}
                        />
                      </div>

                      {/* Max Amount */}
                      <div>
                        <label
                          className="block text-sm mb-2"
                          style={{ color: "#3B4953" }}
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
                            backgroundColor: "#F0F4F8",
                            color: "#000000",
                            border: "1px solid #D0D5DD"
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
                  className="rounded-lg shadow-lg overflow-hidden"
                  style={{
                    backgroundColor: "#FFFFFF",
                    border: "1px solid #D0D5DD"
                  }}
                >
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead style={{ backgroundColor: "#E9EEF6" }}>
                        <tr>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#3B4953" }}
                          >
                            Transaction ID
                          </th>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#3B4953" }}
                          >
                            Status
                          </th>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#3B4953" }}
                          >
                            Amount
                          </th>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#3B4953" }}
                          >
                            Payment Method
                          </th>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#3B4953" }}
                          >
                            Countries
                          </th>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#3B4953" }}
                          >
                            Purpose
                          </th>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#3B4953" }}
                          >
                            Payment Time
                          </th>
                          <th
                            className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider"
                            style={{ color: "#3B4953" }}
                          >
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody style={{ borderTop: "1px solid #D0D5DD" }}>
                        {filteredPaginatedTransactions.map((transaction) => (
                          <tr
                            key={transaction.transaction_id}
                            className="transition-colors hover:opacity-80"
                            style={getRowColor()}
                          >
                            <td
                              className="px-6 py-4 whitespace-nowrap text-sm font-medium"
                              style={{ color: "#000000" }}
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
                              style={{ color: "#3B4953" }}
                            >
                              {transaction.payment_amount
                                ? `${
                                    transaction.currency || ""
                                  } ${transaction.payment_amount.toLocaleString()}`
                                : "N/A"}
                            </td>
                            <td
                              className="px-6 py-4 whitespace-nowrap text-sm"
                              style={{ color: "#3B4953" }}
                            >
                              {transaction.payment_method || "N/A"}
                            </td>
                            <td
                              className="px-6 py-4 text-sm"
                              style={{ color: "#3B4953" }}
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
                              style={{ color: "#3B4953" }}
                            >
                              {transaction.payment_purpose || "N/A"}
                            </td>
                            <td
                              className="px-6 py-4 whitespace-nowrap text-sm"
                              style={{ color: "#3B4953" }}
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
                                  backgroundColor: "#E9EEF6",
                                  color: "#3B4953"
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
                    <p style={{ color: "#3B4953" }}>
                      {activeFilterCount > 0
                        ? "No transactions match the current filters"
                        : "No transactions found"}
                    </p>
                    {activeFilterCount > 0 && (
                      <button
                        onClick={resetFilters}
                        className="mt-4 px-4 py-2 rounded transition-all hover:opacity-80"
                        style={{ backgroundColor: "#E9EEF6", color: "#3B4953" }}
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
                className="fixed right-0 top-0 h-full w-[500px] shadow-lg flex flex-col"
                style={{
                  backgroundColor: "#FFFFFF",
                  borderLeft: "1px solid #D0D5DD"
                }}
              >
                {/* Sticky Header */}
                <div
                  className="sticky top-0 z-10"
                  style={{
                    backgroundColor: "#E9EEF6",
                    borderBottom: "1px solid #D0D5DD"
                  }}
                >
                  {/* Title and Close Button */}
                  <div className="flex items-center justify-between p-6 pb-4">
                    <h2
                      className="text-xl font-bold"
                      style={{ color: "#000000" }}
                    >
                      Transaction Analysis
                    </h2>
                    <button
                      onClick={() => setSelectedTransaction(null)}
                      className="p-2 rounded transition-all hover:opacity-80"
                      style={{ backgroundColor: "#FFFFFF", color: "#3B4953" }}
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>

                  {/* Action Buttons */}
                  {(selectedTransaction.approval_status
                    ?.toLowerCase()
                    .includes("review") ||
                    selectedTransaction.approval_status?.toLowerCase() ===
                      "in review" ||
                    selectedTransaction.approval_status?.toLowerCase() ===
                      "pending") && (
                    <div className="flex gap-3 px-6 pb-4">
                      <button
                        onClick={() =>
                          updateTransactionStatus(
                            selectedTransaction.transaction_id,
                            "Approved"
                          )
                        }
                        className="flex-1 px-4 py-2 rounded font-medium transition-all hover:opacity-90 text-sm"
                        style={{ backgroundColor: "#22c55e", color: "#fff" }}
                      >
                        ✓ Approve
                      </button>
                      <button
                        onClick={() =>
                          updateTransactionStatus(
                            selectedTransaction.transaction_id,
                            "Rejected"
                          )
                        }
                        className="flex-1 px-4 py-2 rounded font-medium transition-all hover:opacity-90 text-sm"
                        style={{ backgroundColor: "#ef4444", color: "#fff" }}
                      >
                        ✗ Reject
                      </button>
                    </div>
                  )}

                  {/* Tabs */}
                  <div
                    className="flex border-b"
                    style={{ borderColor: "#D0D5DD" }}
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
                          color: activeTab === tab.id ? "#3b82f6" : "#3B4953",
                          borderBottom:
                            activeTab === tab.id
                              ? "2px solid #3b82f6"
                              : "2px solid transparent"
                        }}
                      >
                        {tab.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Scrollable Tab Content */}
                <div className="flex-1 overflow-y-auto p-6">
                  {renderTabContent()}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
