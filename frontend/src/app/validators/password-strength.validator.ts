import { AbstractControl, FormGroup, ValidationErrors, Validator, ValidatorFn } from "@angular/forms";


export function passwordStrength(minLength: number): ValidatorFn {

    return (control: AbstractControl): ValidationErrors | null => {

        if (!control.value) return null;

        const regex = /[$-/:-?{}-~!"^_@'\[\]]/g;
        const lowerLetters: boolean = /[a-z]+/.test(control.value);
        const upperLetters: boolean = /[A-Z]+/.test(control.value);
        const numbers: boolean = /[0-9]+/.test(control.value);
        const symbols: boolean = regex.test(control.value);
        const length: boolean = control.value.length >= minLength;

        const valid = lowerLetters && upperLetters && numbers && symbols && length




        let error: string
        if (!length) error = `La password de avere almeno ${minLength} caratteri`;
        else {
            error = valid
                ? null
                : `la password deve contenere almeno ${!lowerLetters ? 'una lettera minuscola' : ''} ${!upperLetters ? 'una lettera maiuscola' : ''} ${!numbers ? 'un numero' : ''} ${!symbols ? 'un simbolo' : ''}`
        }

        // console.log("lowerLetters", lowerLetters)
        // console.log("upperLetters", upperLetters)
        // console.log("numbers", numbers)
        // console.log("symbols", symbols)
        // console.log("length", length)


        return !valid ? { password_strength: error } : null;
    };
}

// ^                         Start anchor
// (?=.*[A-Z].*[A-Z])        Ensure string has two uppercase letters.
// (?=.*[!@#$&*])            Ensure string has one special case letter.
// (?=.*[0-9].*[0-9])        Ensure string has two digits.
// (?=.*[a-z].*[a-z].*[a-z]) Ensure string has three lowercase letters.
// .{8}                      Ensure string is of length 8.
// $                         End anchor.

//   ^(?=.*[A-Z].*[A-Z])(?=.*[!@#$&*])(?=.*[0-9].*[0-9])(?=.*[a-z].*[a-z].*[a-z]).{8}$