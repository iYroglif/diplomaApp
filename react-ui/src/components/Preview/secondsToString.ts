export const secondsToString = (seconds: number): string => {
  const str = `${seconds} секунд`;

  switch (new Intl.PluralRules("ru-RU").select(seconds)) {
    case "one":
      return str + "a";
    case "few":
      return str + "ы";
    default:
      return str;
  }
};
