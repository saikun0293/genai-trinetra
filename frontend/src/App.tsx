import { useState, useEffect } from "react"

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
  [key: string]: any
}

interface TransactionsResponse {
  success: boolean
  count: number
  total: number
  transactions: Transaction[]
}

export default function App() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [totalCount, setTotalCount] = useState<number>(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTransactions()
  }, [])

  const fetchTransactions = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Fetch all transactions by default (fetch_all=true)
      const response = await fetch("/api/getTransactions?fetch_all=true")

      if (!response.ok) {
        throw new Error(`Failed to fetch transactions: ${response.status}`)
      }

      const data: TransactionsResponse = await response.json()
      setTransactions(data.transactions || [])
      setTotalCount(data.total || 0)
    } catch (err) {
      console.error("Error fetching transactions:", err)
      setError(
        err instanceof Error ? err.message : "Failed to fetch transactions"
      )
    } finally {
      setIsLoading(false)
    }
  }

  const getRowColor = (status: string) => {
    const normalizedStatus = status?.toLowerCase() || ""

    if (
      normalizedStatus.includes("approved") ||
      normalizedStatus === "approved"
    ) {
      return "bg-green-50 hover:bg-green-100"
    } else if (
      normalizedStatus.includes("review") ||
      normalizedStatus === "in review" ||
      normalizedStatus === "pending"
    ) {
      return "bg-yellow-50 hover:bg-yellow-100"
    } else {
      return "bg-red-50 hover:bg-red-100"
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
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-neutral-600 border-t-blue-500 rounded-full animate-spin mx-auto"></div>
          <p className="text-xl text-neutral-300">Loading transactions...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-4xl font-bold text-white mb-2">
            Payment Compliance Dashboard
          </h1>
          <div className="flex items-center gap-4 text-neutral-300">
            <p>
              Showing:{" "}
              <span className="font-semibold text-white">
                {transactions.length}
              </span>{" "}
              transactions
            </p>
            <span className="text-neutral-500">•</span>
            <p>
              Total in Database:{" "}
              <span className="font-semibold text-white">{totalCount}</span>
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-800 text-white">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    Transaction ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    Payment Method
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    Countries
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    Purpose
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    Payment Time
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {transactions.map((transaction) => (
                  <tr
                    key={transaction.transaction_id}
                    className={`${getRowColor(
                      transaction.approval_status
                    )} transition-colors`}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {transaction.amount
                        ? `${
                            transaction.currency || ""
                          } ${transaction.amount.toLocaleString()}`
                        : "N/A"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {transaction.payment_method || "N/A"}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      <div className="flex flex-col">
                        <span>From: {transaction.payee_country || "N/A"}</span>
                        <span>To: {transaction.vendor_country || "N/A"}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      {transaction.payment_purpose || "N/A"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {transaction.payment_time || "N/A"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {transactions.length === 0 && (
          <div className="text-center mt-8">
            <p className="text-neutral-400">No transactions found</p>
          </div>
        )}
      </div>
    </div>
  )
}
