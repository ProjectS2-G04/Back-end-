import { useState } from "react";
function Square({ value, onSequareClick }) {
  return (
    <button onClick={onSequareClick} className="square">
      {value}
    </button>
  );
}

export default function Board() {
  const [xIsNext, setxIsNext] = useState(true);
  const [squares, setSquares] = useState(Array(9).fill(null));
  const winner = calculateWinner(squares);
  let status;
  if (winner) {
    status = "Winner" + winner;
  } else {
    status = "Next Player:" + (xIsNext ? "X" : "O");
  }
  function handleClick(i: number) {
    if (squares[i] || calculateWinner(squares)) {
      return;
    }
    const nextSquare = squares.slice();
    if (xIsNext) {
      nextSquare[i] = "X";
    } else {
      nextSquare[i] = "O";
    }
    setSquares(nextSquare);
    setxIsNext(!xIsNext);
  }
  return (
    <>
      <div className="status">{status}</div>
      <div className="board-row">
        <Square onSequareClick={() => handleClick(0)} value={squares[0]} />
        <Square onSequareClick={() => handleClick(1)} value={squares[1]} />
        <Square onSequareClick={() => handleClick(2)} value={squares[2]} />
      </div>
      <div className="board-row">
        <Square onSequareClick={() => handleClick(3)} value={squares[3]} />
        <Square onSequareClick={() => handleClick(4)} value={squares[4]} />
        <Square onSequareClick={() => handleClick(5)} value={squares[5]} />
      </div>
      <div className="board-row">
        <Square onSequareClick={() => handleClick(6)} value={squares[6]} />
        <Square onSequareClick={() => handleClick(7)} value={squares[7]} />
        <Square onSequareClick={() => handleClick(8)} value={squares[8]} />
      </div>
    </>
  );
}
function calculateWinner(squares: any[]) {
  const lines = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
  ];
  for (let i = 0; i < lines.length; i++) {
    const [a, b, c] = lines[i];
    if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
      return squares[a];
    }
  }
  return null;
}
