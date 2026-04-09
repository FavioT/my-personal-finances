export interface Transaction {
  id: number;
  date: string;
  description: string;
  amount: number;
  currency: string;
  category: string | null;
  source: string;
  source_type: 'xls' | 'pdf';
  created_at: string;
}

export interface SummaryResponse {
  total_income: number;
  total_expenses: number;
  balance: number;
}

export interface TransactionFilters {
  source_type?: string;
  date_from?: string;
  date_to?: string;
}
