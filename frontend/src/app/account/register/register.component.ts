import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { NgxErrorsModule } from '@ildug/ngx-errors';
import { AccountService, AuthService } from '../../services';

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

    form = new FormGroup({
        email: new FormControl('', [Validators.required, Validators.email]),
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
        // this.account$.register(email, password)
        //     .subscribe();

    }

}
