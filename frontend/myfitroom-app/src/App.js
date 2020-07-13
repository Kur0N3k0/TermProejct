import React from 'react';
import { Layout, Menu } from 'antd';
import 'antd/dist/antd.css';

const { Header, Footer, Sider, Content } = Layout;

class App extends React.Component {
  render() {
    return (
      <div className="App">
        <Layout>
          <Header>
            <Menu theme="dark" mode="horizontal">
              <Menu.Item key="1">key 1</Menu.Item>
              <Menu.Item key="2">key 2</Menu.Item>
              <Menu.Item key="3">key 3</Menu.Item>
            </Menu>
          </Header>
          <Content>
            Test
          </Content>
        </Layout>
      </div>
    );
  }
}

export default App;
