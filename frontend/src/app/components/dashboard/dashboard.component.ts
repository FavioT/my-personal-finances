import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { BaseChartDirective } from 'ng2-charts';
import { ChartData, ChartType } from 'chart.js';
import { TransactionService } from '../../services/transaction.service';
import { SummaryResponse } from '../../models/transaction.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatProgressSpinnerModule, BaseChartDirective],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  summary: SummaryResponse | null = null;
  loading = true;
  error: string | null = null;

  pieChartType: ChartType = 'pie';
  pieChartData: ChartData<'pie'> = {
    labels: ['Income', 'Expenses'],
    datasets: [{ data: [0, 0], backgroundColor: ['#4caf50', '#f44336'] }],
  };

  constructor(private transactionService: TransactionService) {}

  ngOnInit(): void {
    this.transactionService.getSummary().subscribe({
      next: (data) => {
        this.summary = data;
        this.pieChartData = {
          labels: ['Income', 'Expenses'],
          datasets: [
            {
              data: [data.total_income, Math.abs(data.total_expenses)],
              backgroundColor: ['#4caf50', '#f44336'],
            },
          ],
        };
        this.loading = false;
      },
      error: () => {
        this.error = 'Could not connect to backend. Please make sure the server is running.';
        this.loading = false;
      },
    });
  }
}
