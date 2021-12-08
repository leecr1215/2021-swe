import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import { USER_SERVER } from "../config";
import axios from "axios";
import { useHistory } from "react-router";

const Gallery = () => {
  const [imgList, setImgList] = useState([]);

  useEffect(() => {
    if (window.localStorage.getItem("isAuth") === "true") {
      getImages();
    }
  }, []);

  const getImages = async () => {
    console.log("하이");
    try {
      const response = axios.get(`${USER_SERVER}/satellite/api/showGallery`);
      console.log(response);
      if (response.data.success) {
        //history.push(`/`);
        const realData = response.data.images;
        setImgList(realData);
        console.log(realData[0]);
      }
    } catch (error) {
      alert(error);
    }
  };

  const clickDownloadBtn = () => {};

  const clickDeleteBtn = () => {};

  return (
    <div
      style={{
        backgroundColor: "#FEFEFE",
        width: "100vw",
        minHeight: "88vh",
        marginTop: "80px",
        zIndex: "0",
      }}
      className="window"
    >
      <div className="nav">
        <Header />
        <div className="tableArea">
          <thead>
            <tr>
              <td>선택</td>
              <td>이미지 제목</td>
              <td>영상 타이틀</td>
              <td>영상 촬영 날짜</td>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td></td>
              <td></td>
            </tr>
          </tbody>
        </div>
        <div>
          <button onClick={clickDownloadBtn}>저장</button>
        </div>
        <div>
          <button onClick={clickDeleteBtn}>삭제</button>
        </div>
      </div>
    </div>
  );
};

export default Gallery;
