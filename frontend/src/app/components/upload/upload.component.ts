import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatListModule } from '@angular/material/list';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { UploadService } from '../../services/upload.service';
import { Transaction } from '../../models/transaction.model';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatProgressBarModule,
    MatIconModule,
    MatSnackBarModule,
    MatListModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss'],
})
export class UploadComponent {
  xlsLoading = false;
  xlsResult: Transaction[] | null = null;
  xlsError: string | null = null;

  bbvaText = '';
  bbvaLoading = false;
  bbvaResult: Transaction[] | null = null;
  bbvaError: string | null = null;

  macroText = '';
  macroLoading = false;
  macroResult: Transaction[] | null = null;
  macroError: string | null = null;

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

  onBbvaSubmit(): void {
    if (!this.bbvaText.trim()) return;

    this.bbvaLoading = true;
    this.bbvaResult = null;
    this.bbvaError = null;

    this.uploadService.uploadBbvaText(this.bbvaText).subscribe({
      next: (transactions) => {
        this.bbvaResult = transactions;
        this.bbvaLoading = false;
        this.bbvaText = '';
        this.snackBar.open(`${transactions.length} transactions imported from BBVA`, 'Close', { duration: 4000 });
      },
      error: (err) => {
        this.bbvaError = err.error?.detail ?? 'Error processing BBVA statement.';
        this.bbvaLoading = false;
      },
    });
  }

  onMacroSubmit(): void {
    if (!this.macroText.trim()) return;

    this.macroLoading = true;
    this.macroResult = null;
    this.macroError = null;

    this.uploadService.uploadMacroText(this.macroText).subscribe({
      next: (transactions) => {
        this.macroResult = transactions;
        this.macroLoading = false;
        this.macroText = '';
        this.snackBar.open(`${transactions.length} transactions imported from Macro`, 'Close', { duration: 4000 });
      },
      error: (err) => {
        this.macroError = err.error?.detail ?? 'Error processing Macro statement.';
        this.macroLoading = false;
      },
    });
  }
}
