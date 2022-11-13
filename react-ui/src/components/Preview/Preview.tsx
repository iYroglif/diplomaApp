import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import calcFileSize from "../calcFileSize";
import useFetchBlob from "./useFetchBlob";
import "./Preview.css";
import Processing from "./Processing/Processing";

interface FileProps {
    name: string;
    size: number;
    width: number;
    height: number;
    numframes: number;
}

export default function Preview() {
    const params = useParams();
    const [fileProps, setFileProps] = useState<FileProps | null>(null);
    const [imgOrig, imgOrigError] = useFetchBlob('/api/file-preview/' + params.fileId);
    const [imgDen, imgDenError] = useFetchBlob('/api/file-preview-denoised/' + params.fileId);
    const [isSubmitted, setIsSubmitted] = useState(false);

    useEffect(() => {
        let ignore = false;

        fetch('/api/file-props/' + params.fileId)
            .then((res) => {
                if (res.ok)
                    return res.json();
                else
                    throw new Error('Файл не найден');
            })
            .then(
                (data) => {
                    if (!ignore) {
                        setFileProps(data);
                    }
                },
                (e) => {
                    if (!ignore) {
                        setFileProps(null);
                        console.error(e);
                        // @TODO обработка того что файл не найден на сервере
                    }
                }
            )

        return () => {
            ignore = true;
        };
    }, [params.fileId])

    let imgOrigUrl = null;
    if (imgOrigError) {
        console.error(imgOrigError);
        // @TODO обработка того что файл не найден на сервере
    } else if (imgOrig) {
        imgOrigUrl = URL.createObjectURL(imgOrig);
    }

    let imgDenUrl = null;
    if (imgDenError) {
        console.error(imgDenError);
        // @TODO обработка того что файл не найден на сервере
    } else if (imgDen) {
        imgDenUrl = URL.createObjectURL(imgDen);
    }

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
                                    {imgOrigUrl && (<img src={imgOrigUrl} alt="Исходный кадр" />)}
                                    <p>Размер файла: {calcFileSize(fileProps.size)}</p>
                                </div>
                                <div className="file-preview-denoised">
                                    <p>Превью обработки файла:</p>
                                    {imgDenUrl && (<img src={imgDenUrl} alt="Обработанный кадр" />)}
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
    );
}