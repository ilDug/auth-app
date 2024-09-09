import { Routes } from '@angular/router';
import { LoginComponent } from './account/login/login.component';
import { AccountComponent } from './account/account.component';

export const routes: Routes = [
    { path: '', redirectTo: 'account', pathMatch: 'full' },
    {
        path: 'account',
        component: AccountComponent,
        children: [
            { path: '', redirectTo: 'login', pathMatch: 'full' },
            { path: 'login', component: LoginComponent },
        ]
    }
];
