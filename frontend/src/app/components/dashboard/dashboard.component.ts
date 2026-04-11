import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { BaseChartDirective } from 'ng2-charts';
import { ChartData, ChartType } from 'chart.js';
import { TransactionService } from '../../services/transaction.service';
import { SummaryResponse } from '../../models/transaction.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, BaseChartDirective],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  summary: SummaryResponse | null = null;
  loading = true;
  error: string | null = null;

  pieChartType: ChartType = 'pie';
  pieChartData: ChartData<'pie'> = {
    labels: ['Ingresos', 'Gastos'],
    datasets: [{ data: [0, 0], backgroundColor: ['#00A800', '#A80000'] }],
  };

  constructor(private transactionService: TransactionService) {}

  ngOnInit(): void {
    this.transactionService.getSummary().subscribe({
      next: (data) => {
        this.summary = data;
        this.pieChartData = {
          labels: ['Ingresos', 'Gastos'],
          datasets: [{ data: [data.total_income, Math.abs(data.total_expenses)], backgroundColor: ['#00A800', '#A80000'] }],
        };
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudo conectar al servidor. Verificá que el backend esté corriendo.';
        this.loading = false;
      },
    });
  }
}
