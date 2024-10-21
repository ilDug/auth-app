import { AbstractControl, AsyncValidatorFn, ValidationErrors } from "@angular/forms";
import { debounce, debounceTime, map, Observable } from "rxjs";
import { AccountService } from "../services";

/**
 * Checks if an email exists to validate the email field
 * @param accountService Service that checks if an email exists
 * @returns Email exists async validator
 */
export const emailExistsAsyncValidator = (accountService: AccountService): AsyncValidatorFn => {
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
        return accountService.emailExists(control.value)
            .pipe(
                map(exists => exists ? { emailExists: true } : null)
            );
    }
}