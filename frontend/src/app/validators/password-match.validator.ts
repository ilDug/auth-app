import { AbstractControl, FormGroup, ValidationErrors, Validator, ValidatorFn } from "@angular/forms";


export const passwordMatchValidator = (controlName: string, matchingControlName: string): ValidatorFn => {

    return (form: FormGroup): ValidationErrors => {
        const control: AbstractControl = form.controls[controlName];
        const matchingControl: AbstractControl = form.controls[matchingControlName];

        /** previene il controllo per la presenza di altri errori */
        if (control.errors && !matchingControl.errors["notMatch"]) {
            return null;
        }

        if (control.value === matchingControl.value) {
            matchingControl.setErrors(null)
            return null;
        }
        else {
            matchingControl.setErrors({ notMatch: true })
            return { fieldsNotMaching: true }
        }
    }
}

