export interface CreditCardInstallmentItem {
  transaction_id: number;
  description: string;
  date: string;
  monthly_amount: number;
  installment_current: number;
  installment_total: number;
  pending_installments: number;
  remaining_debt: number;
  total_debt: number;
  payoff_month: string; // "YYYY-MM"
}

export interface CardSummary {
  card: string;
  card_network: string;
  total_monthly: number;
  total_remaining_debt: number;
  total_debt: number;
  payoff_month: string;
  items: CreditCardInstallmentItem[];
}

export interface CreditCardSummaryResponse {
  cards: CardSummary[];
}
