import { useEffect, useState } from "react";

export default function useFetchJSON<Type>(url: string): [Type | null, Error | null] {
    const [data, setData] = useState<Type | null>(null);
    const [error, setError] = useState<Error | null>(null);

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
                        setError(null);
                    }
                },
                (error) => {
                    if (!ignore) {
                        setError(error);
                        setData(null);
                    }
                }
            )

        return () => {
            ignore = true;
        };
    }, [url]);

    return [data, error];
};