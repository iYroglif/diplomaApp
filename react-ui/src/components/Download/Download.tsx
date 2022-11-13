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
                <div className="download">
                    <h3>Скачивание файла начнется автоматически, если нет нажмите на кнопку:</h3>
                    <a className="link" href={"/api/download/" + params.fileId}>
                        <div className="download-btn">Скачать файл</div>
                    </a>
                </div>
            ) : (
                <>
                    <p>Файл не существует</p>
                </>
            )}
        </>
    );
}