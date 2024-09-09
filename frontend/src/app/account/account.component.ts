import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
    selector: 'auth-account',
    standalone: true,
    imports: [RouterOutlet],
    template: `
    <div class="flex flex-center">
        <router-outlet />
    </div>
    `,
})
export class AccountComponent {

}
