
const apiServerPort = '8080';

const getLocation = () => {
  alert(window.location.port)
  const isDeployedFromApiServer = (window.location.port === apiServerPort);
  return ((isDeployedFromApiServer) ? '' : `http://localhost:${apiServerPort}`);
}

export const getApiPath = (endpoint) => {
  return (getLocation() ? `${getLocation()}/api/v1/${endpoint}` : `api/v1/${endpoint}`);
};