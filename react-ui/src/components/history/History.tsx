import { useEffect, useState } from "react";
import { TaskRow } from "./TaskRow";
import "./History.css";
import TaskRowProps from "./TaskRowPropsInterface";

export default function History() {
    const [rows, setRows] = useState<JSX.Element[]>([])

    useEffect(() => {
        fetch('/api/history')
            .then((res) => {
                if (res.ok)
                    return res.json()
            })
            .then((data) => {
                const tempRows: JSX.Element[] = []
                data.tasks.forEach((row: TaskRowProps) => {
                    tempRows.push(
                        <TaskRow {...row} />
                    )
                });
                setRows(tempRows)
            })
    }, [])

    return (
        <div className="history">
            <table className="table">
                <thead className="table table-striped">
                    <tr>
                        <th scope="col">Название файла</th>
                        <th scope="col">Размер</th>
                        <th scope="col">Дата и время</th>
                        <th scope="col"></th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    );
}