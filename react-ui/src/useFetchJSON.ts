import { useEffect, useState } from "react";

export const useFetchJSON = <Type>(url: string): [Type | undefined, Error | undefined] => {
  const [data, setData] = useState<Type>();
  const [error, setError] = useState<Error>();

  useEffect(() => {
    let ignore = false;

    fetch(url)
      .then((res) => {
        if (res.ok) {
          return res.json();
        }

        throw new Error("Ошибка запроса");
      })
      .then(
        (data) => {
          if (!ignore) {
            setData(data);
            setError(undefined);
          }
        },
        (error) => {
          if (!ignore) {
            setError(error);
            setData(undefined);
          }
        }
      );

    return () => {
      ignore = true;
    };
  }, [url]);

  return [data, error];
};
