import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { NgxErrorsModule } from '@ildug/ngx-errors';
import { AccountService, AuthService } from '../../services';
import { ActivatedRoute, Router } from '@angular/router';
import { filter, finalize, map, switchMap, tap } from 'rxjs';

@Component({
    selector: 'auth-login',
    standalone: true,
    imports: [NgxErrorsModule, ReactiveFormsModule],
    templateUrl: './login.component.html',
    styles: ``
})
export class LoginComponent {

    auth = inject(AuthService);
    account$ = inject(AccountService);
    route = inject(ActivatedRoute);

    form = new FormGroup({
        email: new FormControl('', [Validators.required, Validators.email]),
        password: new FormControl('', [Validators.required, Validators.minLength(8)])
    })

    /**
     * Logs in the user.
     */
    login() {
        // If the form is invalid, stop here
        if (this.form.invalid) return;

        // Extract the email and password from the form
        const { email, password } = this.form.value;

        // Log in the user
        this.account$.login(email, password)
            .pipe(
                // filter out unsuccessful logins
                filter(success => success),
                // Get the returnUrl query parameter
                switchMap(() => this.route.queryParams),
                // Extract the returnUrl query parameter
                map(({ returnUrl }) => returnUrl || '/'),
                // Redirect to the returnUrl query parameter if it exists, otherwise redirect to the home page.
                tap(url => location.href = url),
                // Reset the form
                finalize(() => this.form.reset())
            )
            .subscribe();
    }

}
