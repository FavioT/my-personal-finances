import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatListModule } from '@angular/material/list';
import { UploadService } from '../../services/upload.service';
import { Transaction } from '../../models/transaction.model';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatCardModule,
    MatProgressBarModule,
    MatIconModule,
    MatSnackBarModule,
    MatListModule,
  ],
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss'],
})
export class UploadComponent {
  xlsLoading = false;
  pdfLoading = false;
  xlsResult: Transaction[] | null = null;
  pdfResult: Transaction[] | null = null;
  xlsError: string | null = null;
  pdfError: string | null = null;

  constructor(private uploadService: UploadService, private snackBar: MatSnackBar) {}

  onXlsFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    this.xlsLoading = true;
    this.xlsResult = null;
    this.xlsError = null;

    this.uploadService.uploadXls(file).subscribe({
      next: (transactions) => {
        this.xlsResult = transactions;
        this.xlsLoading = false;
        this.snackBar.open(`${transactions.length} transactions imported from XLS`, 'Close', { duration: 4000 });
      },
      error: (err) => {
        this.xlsError = err.error?.detail ?? 'Error uploading file.';
        this.xlsLoading = false;
      },
    });
  }

  onPdfFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    this.pdfLoading = true;
    this.pdfResult = null;
    this.pdfError = null;

    this.uploadService.uploadPdf(file).subscribe({
      next: (transactions) => {
        this.pdfResult = transactions;
        this.pdfLoading = false;
        this.snackBar.open(`${transactions.length} transactions imported from PDF`, 'Close', { duration: 4000 });
      },
      error: (err) => {
        this.pdfError = err.error?.detail ?? 'Error uploading file.';
        this.pdfLoading = false;
      },
    });
  }
}
