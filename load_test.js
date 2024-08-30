import http from 'k6/http';
import { sleep } from 'k6';

const modelUrl = 'http://localhost:8000/models';

export function setup() {
  const modelsres = JSON.parse(http.get(modelUrl).body);
  return { modelList: modelsres.models };
}

export default function (data) {
  const modelList = data.modelList;
  const randomModel = modelList[Math.floor(Math.random() * modelList.length)];
  const url = 'http://localhost:8000/infer';
  const payload = JSON.stringify({
    model: randomModel,
    text: 'こんにちはー。げんきっすかー？私は元気ですよー。'
  });
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  http.post(url, payload, params);
  sleep(1);
}