import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { NgxErrorsModule } from '@ildug/ngx-errors';
import { AccountService, AuthService } from '../../services';
import { filter, finalize, tap } from 'rxjs';
import { NgxToastService } from '@ildug/ngx-toast';
import { emailExistsAsyncValidator } from '../../validators';

@Component({
    selector: 'auth-register',
    standalone: true,
    imports: [NgxErrorsModule, ReactiveFormsModule, RouterLink],
    templateUrl: './register.component.html',
    styles: ``
})
export class RegisterComponent {

    auth = inject(AuthService);
    account$ = inject(AccountService);
    toast = inject(NgxToastService);
    success = signal<boolean>(false);

    form = new FormGroup({
        email: new FormControl('', [Validators.required, Validators.email], [emailExistsAsyncValidator(this.account$)]),
        password: new FormControl('', [Validators.required, Validators.minLength(8)]),
        terms: new FormControl(false, [Validators.requiredTrue])
    })

    /**
     * Registers the user.
     */
    register() {
        // If the form is invalid, stop here
        if (this.form.invalid) return;

        // Extract the email, password, and terms from the form
        const { email, password } = this.form.value;

        // Register the user
        this.account$.register(email, password)
            .pipe(
                // filter out unsuccessful registrations
                filter(success => success),
                // show the success message
                tap(() => this.toast.info(`Registrazione effettuata con successo!`)),
                // set the success signal to true
                tap(() => this.success.set(true)),
                // update the email field validity
                finalize(() => this.form.get('email').updateValueAndValidity()),
                // Reset the form
                finalize(() => this.form.reset())
            )
            .subscribe();

    }

}
