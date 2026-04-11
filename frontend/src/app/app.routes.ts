import { Routes } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { TransactionsComponent } from './components/transactions/transactions.component';
import { UploadComponent } from './components/upload/upload.component';
import { CreditCardsComponent } from './components/credit-cards/credit-cards.component';

export const routes: Routes = [
  { path: 'dashboard', component: DashboardComponent },
  { path: 'transactions', component: TransactionsComponent },
  { path: 'upload', component: UploadComponent },
  { path: 'credit-cards', component: CreditCardsComponent },
  { path: '**', redirectTo: 'dashboard' },
];
