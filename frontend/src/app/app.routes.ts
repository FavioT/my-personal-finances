import { Routes } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { TransactionsComponent } from './components/transactions/transactions.component';
import { UploadComponent } from './components/upload/upload.component';

export const routes: Routes = [
  { path: 'dashboard', component: DashboardComponent },
  { path: 'transactions', component: TransactionsComponent },
  { path: 'upload', component: UploadComponent },
  { path: '**', redirectTo: 'dashboard' },
];
