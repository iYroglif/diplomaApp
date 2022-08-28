import { useEffect, useState } from "react";
import { Processing } from "./Processing";
import "./Preview.css"
import { useParams } from "react-router-dom";

export const calcFileSize = (size: number) => {
    if (size < 1024) {
        return size + 'bytes';
    } else if (size > 1024 && size < 1048576) {
        return (size / 1024).toFixed(1) + ' KB';
    } else if (size > 1048576) {
        return (size / 1048576).toFixed(1) + ' MB';
    }
}

interface IFileProps {
    name: string
    size: number
    width: number
    height: number
    numframes: number
}

export const Preview = () => {
    const params = useParams()
    const [fileProps, setFileProps] = useState<IFileProps | null>(null)
    const [imgOrigUrl, setImgOrigUrl] = useState<string | null>(null)
    const [imgDenUrl, setImgDenUrl] = useState<string | null>(null)
    const [isSubmitted, setIsSubmitted] = useState(false)

    useEffect(() => {
        fetch('/api/file-props/' + params.fileId)
            .then((res) => {
                if (res.ok)
                    return res.json()
                else
                    throw new Error('Файл не найден')
            })
            .then((data) => setFileProps(data))
            .catch((e) => {
                setFileProps(null)
                console.error(e)
                // @TODO обработка того что файл не найден на сервере
            })
    }, [params.fileId])

    useEffect(() => {
        fetch('/api/file-preview/' + params.fileId)
            .then((res) => {
                if (res.ok)
                    return res.blob()
                else
                    throw new Error('Файл не найден')
            })
            .then((data) => setImgOrigUrl(URL.createObjectURL(data)))
            .catch((e) => {
                console.error(e)
                // @TODO обработка того что файл не найден на сервере
            })
    }, [params.fileId])

    useEffect(() => {
        fetch('/api/file-preview-denoised/' + params.fileId)
            .then((res) => {
                if (res.ok)
                    return res.blob()
                else
                    throw new Error('Файл не найден')
            })
            .then((data) => setImgDenUrl(URL.createObjectURL(data)))
            .catch((e) => {
                console.error(e)
                // @TODO обработка того что файл не найден на сервере
            })
    }, [params.fileId])

    return (
        <>
            {params.fileId && fileProps ? (
                <>
                    {isSubmitted ? (
                        <Processing fileId={params.fileId} />
                    ) : (
                        <div className="preview">
                            <div className="preview-imgs">
                                <div className="file-preview">
                                    <p>Имя файла: {fileProps.name}</p>
                                    {imgOrigUrl && (<img src={imgOrigUrl} />)}
                                    <p>Размер файла: {calcFileSize(fileProps.size)}</p>
                                </div>
                                <div className="file-preview-denoised">
                                    <p>Превью обработки файла:</p>
                                    {imgDenUrl && (<img src={imgDenUrl} />)}
                                </div>
                            </div>
                            <div className="preview-subm">
                                <p>Примерное время обработки: {Math.round(fileProps.height * fileProps.width * fileProps.numframes / 103000)} секунд</p>
                                <div className="btn-start" onClick={() => setIsSubmitted(true)}>Удалить шум</div>
                            </div>
                        </div>
                    )}
                </>
            ) : (
                <p>Файл не существует</p>
            )}
        </>
    )
}