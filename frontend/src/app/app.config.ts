import { ApplicationConfig, LOCALE_ID, provideExperimentalZonelessChangeDetection } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { routes } from './app.routes';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { logInterceptor } from './interceptors/log.interceptor';
import { xErrorsInterceptor } from './interceptors/x-errors.interceptor';
import { authInterceptor } from './interceptors/auth.interceptor';
import { AUTH_SERVER, AUTH_TOKEN } from './injection-tokens';
import { APP_BASE_HREF, PlatformLocation } from '@angular/common';

/** Locale configuration ***************************/
import { registerLocaleData } from '@angular/common';
import localeIt from '@angular/common/locales/it';
registerLocaleData(localeIt);
/************************************************* */

export const appConfig: ApplicationConfig = {
    providers: [
        provideExperimentalZonelessChangeDetection(),
        provideRouter(routes, withComponentInputBinding()),
        provideHttpClient(withInterceptors([
            logInterceptor,
            xErrorsInterceptor,
            authInterceptor
        ])),
        provideAnimationsAsync(),
        { provide: AUTH_TOKEN, useValue: 'dagjwt' },
        { provide: APP_BASE_HREF, useFactory: (pl: PlatformLocation) => pl.getBaseHrefFromDOM(), deps: [PlatformLocation] },
        { provide: LOCALE_ID, useValue: 'it-IT' }
    ]
};
