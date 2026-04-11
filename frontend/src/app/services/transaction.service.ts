import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Transaction, SummaryResponse, TransactionFilters } from '../models/transaction.model';
import { CreditCardSummaryResponse } from '../models/credit-card-summary.model';

const API_URL = 'http://localhost:8000';

@Injectable({
  providedIn: 'root',
})
export class TransactionService {
  constructor(private http: HttpClient) {}

  getTransactions(filters?: TransactionFilters): Observable<Transaction[]> {
    let params = new HttpParams();
    if (filters?.source_type) {
      params = params.set('source_type', filters.source_type);
    }
    if (filters?.date_from) {
      params = params.set('date_from', filters.date_from);
    }
    if (filters?.date_to) {
      params = params.set('date_to', filters.date_to);
    }
    return this.http.get<Transaction[]>(`${API_URL}/transactions`, { params });
  }

  getSummary(): Observable<SummaryResponse> {
    return this.http.get<SummaryResponse>(`${API_URL}/transactions/summary`);
  }

  deleteTransaction(id: number): Observable<void> {
    return this.http.delete<void>(`${API_URL}/transactions/${id}`);
  }

  getCreditCardSummary(): Observable<CreditCardSummaryResponse> {
    return this.http.get<CreditCardSummaryResponse>(`${API_URL}/transactions/credit-card-summary`);
  }
}
