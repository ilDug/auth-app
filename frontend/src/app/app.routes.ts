import { Routes } from '@angular/router';
import { LoginComponent } from './account/login/login.component';
import { AccountComponent } from './account/account.component';
import { RegisterComponent } from './account/register/register.component';
import { ActivateComponent } from './account/activate/activate.component';

export const routes: Routes = [
    { path: '', redirectTo: 'account', pathMatch: 'full' },
    {
        path: 'account',
        component: AccountComponent,
        children: [
            { path: '', redirectTo: 'login', pathMatch: 'full' },
            { path: 'login', component: LoginComponent, title: 'Login' },
            { path: 'register', component: RegisterComponent, title: 'Register' },
            { path: 'activate/:key', component: ActivateComponent, title: 'Activate' },
        ]
    },
];
