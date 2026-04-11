import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TransactionService } from '../../services/transaction.service';
import { CardSummary } from '../../models/credit-card-summary.model';

@Component({
  selector: 'app-credit-cards',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
  ],
  templateUrl: './credit-cards.component.html',
  styleUrls: ['./credit-cards.component.scss'],
})
export class CreditCardsComponent implements OnInit {
  cards: CardSummary[] = [];
  loading = true;
  error: string | null = null;

  constructor(private transactionService: TransactionService) {}

  ngOnInit(): void {
    this.transactionService.getCreditCardSummary().subscribe({
      next: (data) => {
        this.cards = data.cards;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Error al cargar el resumen de tarjetas';
        this.loading = false;
      },
    });
  }

  formatMonth(ym: string): string {
    if (!ym) return '-';
    const [year, m] = ym.split('-');
    const names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    return `${names[parseInt(m, 10) - 1]} ${year}`;
  }
}
