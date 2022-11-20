import { useEffect } from "react"
import { useParams } from "react-router-dom"
import "./Download.css"

export default function Download() {
    const params = useParams();

    useEffect(() => {
        document.location.href = "/api/download/" + params.fileId;
    }, [params.fileId])

    return (
        <>
            {params.fileId ? (
                <>
                    <h3>Скачивание файла начнется автоматически, если нет нажмите на кнопку:</h3>
                    <a className="download-btn" href={"/api/download/" + params.fileId}>
                        Скачать файл
                    </a>
                </>
            ) : (
                <>
                    <p>Файл не существует</p>
                </>
            )}
        </>
    );
}