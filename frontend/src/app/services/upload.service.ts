import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Transaction } from '../models/transaction.model';

const API_URL = 'http://localhost:8000';

@Injectable({
  providedIn: 'root',
})
export class UploadService {
  constructor(private http: HttpClient) {}

  uploadXls(file: File): Observable<Transaction[]> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<Transaction[]>(`${API_URL}/upload/xls`, formData);
  }

  uploadPdf(file: File): Observable<Transaction[]> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<Transaction[]>(`${API_URL}/upload/pdf`, formData);
  }
}
