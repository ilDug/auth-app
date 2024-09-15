import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NgxToastModule } from '@ildug/ngx-toast';

@Component({
    selector: 'auth-root',
    standalone: true,
    imports: [RouterOutlet, NgxToastModule],
    template: `
    <div class="flex flex-col grow" dagToast>
        <router-outlet />
    </div>
  `,
    styles: [],
})
export class AppComponent {
}
