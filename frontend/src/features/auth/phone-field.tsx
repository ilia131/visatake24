import { useId, useState } from "react";
import {
  getCountries,
  getCountryCallingCode,
  parsePhoneNumberFromString,
  type CountryCode,
} from "libphonenumber-js/max";
import { latinDigits } from "../../lib/format";

const persian = new Intl.DisplayNames(["fa"], { type: "region" });
const english = new Intl.DisplayNames(["en"], { type: "region" });
const countries = getCountries().map((code) => ({
  code,
  name: persian.of(code) ?? code,
  englishName: english.of(code) ?? code,
  callingCode: "+" + getCountryCallingCode(code),
  flag: String.fromCodePoint(...Array.from(code, (letter) => letter.charCodeAt(0) + 127397)),
})).sort((first, second) => first.name.localeCompare(second.name, "fa"));

export function validPhone(value: string, country: CountryCode) {
  const phone = parsePhoneNumberFromString(value, { defaultCountry: country, extract: false });
  return phone?.country === country && phone.isValid();
}

type Props = {
  country: CountryCode;
  number: string;
  onCountryChange: (country: CountryCode) => void;
  onNumberChange: (number: string) => void;
};

export function PhoneField({ country, number, onCountryChange, onNumberChange }: Props) {
  const id = useId();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const selected = countries.find(({ code }) => code === country)!;
  const search = latinDigits(query).trim().toLowerCase().replace(/ي/g, "ی").replace(/ك/g, "ک");
  const matches = countries.filter(({ name, englishName, callingCode, code }) =>
    [name, englishName.toLowerCase(), callingCode, code.toLowerCase()].some((value) => value.includes(search)),
  );

  return (
    <div className="phone-field">
      <div className="phone-country" onKeyDown={(event) => {
        if (event.key === "Escape") {
          setOpen(false);
          event.currentTarget.querySelector("button")?.focus();
        }
      }}>
        <button type="button" className="phone-country-button" aria-expanded={open}
          aria-controls={id} onClick={() => { setOpen(!open); setQuery(""); }}>
          <span aria-hidden="true">{selected.flag}</span> {selected.name} <bdi>{selected.callingCode}</bdi>
        </button>
        {open && <div className="phone-country-options" id={id}>
          <input autoFocus type="search" aria-label="جست‌وجوی کشور" placeholder="نام کشور یا کد تلفن"
            value={query} onChange={(event) => setQuery(event.target.value)} />
          <ul>
            {matches.map((item) => <li key={item.code}>
              <button type="button" aria-pressed={item.code === country} onClick={() => {
                onCountryChange(item.code);
                setOpen(false);
                document.getElementById(id + "-number")?.focus();
              }}>
                <span aria-hidden="true">{item.flag}</span> {item.name} <bdi>{item.callingCode}</bdi>
              </button>
            </li>)}
          </ul>
          {!matches.length && <p>کشوری پیدا نشد.</p>}
        </div>}
      </div>
      <label htmlFor={id + "-number"}>
        شماره تلفن
        <span className="phone-number" dir="ltr">
          <bdi>{selected.callingCode}</bdi>
          <input id={id + "-number"} type="tel" inputMode="numeric" autoComplete="tel-national"
            required maxLength={20} value={number}
            onChange={(event) => onNumberChange(latinDigits(event.target.value).replace(/[^0-9]/g, ""))} />
        </span>
      </label>
    </div>
  );
}
