import { useEffect, useState } from "react";

export const useFetchBlob = (url: string): [Blob | null, Error | null] => {
  const [blob, setBlob] = useState<Blob | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let ignore = false;

    fetch(url)
      .then((res) => {
        if (res.ok) {
          return res.blob();
        }

        throw new Error("Ошибка запроса");
      })
      .then(
        (blob) => {
          if (!ignore) {
            setBlob(blob);
            setError(null);
          }
        },
        (error) => {
          if (!ignore) {
            setError(error);
            setBlob(null);
          }
        }
      );

    return () => {
      ignore = true;
    };
  }, [url]);

  return [blob, error];
};
