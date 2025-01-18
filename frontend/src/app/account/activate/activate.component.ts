import { Component, effect, inject, input, OnChanges, signal } from '@angular/core';
import { AccountService } from '../../services';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';

@Component({
    selector: 'auth-activate',
    standalone: true,
    imports: [RouterLink],
    templateUrl: './activate.component.html',
    styles: ``
})
export class ActivateComponent implements OnChanges {
    key = input<string>();
    account$ = inject(AccountService);
    success = signal<boolean>(false);
    message = signal<string | null>(null);

    ngOnChanges() {
        if (!this.key()) return;
        this.account$.activate(this.key())
            .subscribe(result => {
                this.message.set(result.message);
                this.success.set(result.success);
            });
    }
}
