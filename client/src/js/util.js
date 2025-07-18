
const apiServerPort = '8080';

const getLocation = () => {
  const isDeployedFromApiServer = (!window.location.port || (window.location.port === apiServerPort));
  return ((isDeployedFromApiServer) ? '' : `http://localhost:${apiServerPort}`);
}

export const getApiPath = (endpoint) => {
  return (getLocation() ? `${getLocation()}/api/v1/${endpoint}` : `api/v1/${endpoint}`);
};