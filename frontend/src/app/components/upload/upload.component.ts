import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UploadService } from '../../services/upload.service';
import { Transaction } from '../../models/transaction.model';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, FormsModule],
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

  bbvaVisaText = '';
  bbvaVisaLoading = false;
  bbvaVisaResult: Transaction[] | null = null;
  bbvaVisaError: string | null = null;

  bbvaMastercardText = '';
  bbvaMastercardLoading = false;
  bbvaMastercardResult: Transaction[] | null = null;
  bbvaMastercardError: string | null = null;

  macroText = '';
  macroLoading = false;
  macroResult: Transaction[] | null = null;
  macroError: string | null = null;

  constructor(private uploadService: UploadService) {}

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
      },
      error: (err) => {
        this.xlsError = err.error?.detail ?? 'Error al subir el archivo.';
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
      },
      error: (err) => {
        this.bbvaError = err.error?.detail ?? 'Error processing BBVA statement.';
        this.bbvaLoading = false;
      },
    });
  }

  onBbvaVisaSubmit(): void {
    if (!this.bbvaVisaText.trim()) return;

    this.bbvaVisaLoading = true;
    this.bbvaVisaResult = null;
    this.bbvaVisaError = null;

    this.uploadService.uploadBbvaVisaText(this.bbvaVisaText).subscribe({
      next: (transactions) => {
        this.bbvaVisaResult = transactions;
        this.bbvaVisaLoading = false;
        this.bbvaVisaText = '';
      },
      error: (err) => {
        this.bbvaVisaError = err.error?.detail ?? 'Error al procesar el resumen BBVA VISA.';
        this.bbvaVisaLoading = false;
      },
    });
  }

  onBbvaMastercardSubmit(): void {
    if (!this.bbvaMastercardText.trim()) return;

    this.bbvaMastercardLoading = true;
    this.bbvaMastercardResult = null;
    this.bbvaMastercardError = null;

    this.uploadService.uploadBbvaMastercardText(this.bbvaMastercardText).subscribe({
      next: (transactions) => {
        this.bbvaMastercardResult = transactions;
        this.bbvaMastercardLoading = false;
        this.bbvaMastercardText = '';
      },
      error: (err) => {
        this.bbvaMastercardError = err.error?.detail ?? 'Error al procesar el resumen BBVA Mastercard.';
        this.bbvaMastercardLoading = false;
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
      },
      error: (err) => {
        this.macroError = err.error?.detail ?? 'Error al procesar el resumen Macro.';
        this.macroLoading = false;
      },
    });
  }
}
