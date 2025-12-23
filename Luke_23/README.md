# Cookie clicker

**Author**: Shirajuki
**Description**:
> Klarer du å samle inn 1 000 000 000 julecookies for å få den hemmelige gaven Cyberlandslagsnissen har gjemt? Applikasjonen er visstnok laget med et "blazingly" raskt rammeverk, men ting kan alltid gå litt galt nå som nissen er borte...

**Target**: <https://cookie-clicker.julec.tf>

**Framework**: Blazor WebAssembly (webcil-embedded managed assembly).

**Goal**: Trigger the “prize” check (1,000,000,000 clicks) without actually clicking.

## Approach

The page loads `chall.wasm` (webcil container). The UI text just renders an in-memory counter. The real gate is in `chall.Pages.Home:HandleClick`: when `count >= 1_000_000_000`, it calls `DecryptFlag()`. No browser cookies or local storage are involved.

Blazor exposes a low-level hook to call any managed method, even if it isn’t marked `[JSInvokable]`.

## Exploit

```js
const getFlag = Module.mono_bind_static_method("[chall] chall.Pages.Home:DecryptFlag");
console.log(getFlag(1_000_000_000));
```

This bypasses the click loop and invokes the same method the app would run after a billion clicks.

## Flag

`JUL{w3bc1l_1s_just_4_wr4pp3r_f0r_dlls_4nd_d3c0mp1l1ng_th3m_1s_n0t_d1ff1cult}`
