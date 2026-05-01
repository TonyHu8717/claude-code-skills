---
name: web3-testing
description: 使用 Hardhat 和 Foundry 全面测试智能合约，包括单元测试、集成测试和主网分叉。适用于测试 Solidity 合约、设置区块链测试套件或验证 DeFi 协议。
---

# Web3 智能合约测试

掌握使用 Hardhat、Foundry 和高级测试模式的智能合约全面测试策略。

## 何时使用此技能

- 编写智能合约的单元测试
- 设置集成测试套件
- 进行 gas 优化测试
- 模糊测试边界情况
- 分叉主网进行真实测试
- 自动化测试覆盖率报告
- 在 Etherscan 上验证合约

## Hardhat 测试设置

```javascript
// hardhat.config.js
require("@nomicfoundation/hardhat-toolbox");
require("@nomiclabs/hardhat-etherscan");
require("hardhat-gas-reporter");
require("solidity-coverage");

module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    hardhat: {
      forking: {
        url: process.env.MAINNET_RPC_URL,
        blockNumber: 15000000,
      },
    },
    goerli: {
      url: process.env.GOERLI_RPC_URL,
      accounts: [process.env.PRIVATE_KEY],
    },
  },
  gasReporter: {
    enabled: true,
    currency: "USD",
    coinmarketcap: process.env.COINMARKETCAP_API_KEY,
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY,
  },
};
```

## 单元测试模式

```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");
const {
  loadFixture,
  time,
} = require("@nomicfoundation/hardhat-network-helpers");

describe("Token Contract", function () {
  // 测试设置的 Fixture
  async function deployTokenFixture() {
    const [owner, addr1, addr2] = await ethers.getSigners();

    const Token = await ethers.getContractFactory("Token");
    const token = await Token.deploy();

    return { token, owner, addr1, addr2 };
  }

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      const { token, owner } = await loadFixture(deployTokenFixture);
      expect(await token.owner()).to.equal(owner.address);
    });

    it("Should assign total supply to owner", async function () {
      const { token, owner } = await loadFixture(deployTokenFixture);
      const ownerBalance = await token.balanceOf(owner.address);
      expect(await token.totalSupply()).to.equal(ownerBalance);
    });
  });

  describe("Transactions", function () {
    it("Should transfer tokens between accounts", async function () {
      const { token, owner, addr1 } = await loadFixture(deployTokenFixture);

      await expect(token.transfer(addr1.address, 50)).to.changeTokenBalances(
        token,
        [owner, addr1],
        [-50, 50],
      );
    });

    it("Should fail if sender doesn't have enough tokens", async function () {
      const { token, addr1 } = await loadFixture(deployTokenFixture);
      const initialBalance = await token.balanceOf(addr1.address);

      await expect(
        token.connect(addr1).transfer(owner.address, 1),
      ).to.be.revertedWith("Insufficient balance");
    });

    it("Should emit Transfer event", async function () {
      const { token, owner, addr1 } = await loadFixture(deployTokenFixture);

      await expect(token.transfer(addr1.address, 50))
        .to.emit(token, "Transfer")
        .withArgs(owner.address, addr1.address, 50);
    });
  });

  describe("Time-based tests", function () {
    it("Should handle time-locked operations", async function () {
      const { token } = await loadFixture(deployTokenFixture);

      // 时间增加 1 天
      await time.increase(86400);

      // 测试时间相关的功能
    });
  });

  describe("Gas optimization", function () {
    it("Should use gas efficiently", async function () {
      const { token } = await loadFixture(deployTokenFixture);

      const tx = await token.transfer(addr1.address, 100);
      const receipt = await tx.wait();

      expect(receipt.gasUsed).to.be.lessThan(50000);
    });
  });
});
```

## Foundry 测试（Forge）

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/Token.sol";

contract TokenTest is Test {
    Token token;
    address owner = address(1);
    address user1 = address(2);
    address user2 = address(3);

    function setUp() public {
        vm.prank(owner);
        token = new Token();
    }

    function testInitialSupply() public {
        assertEq(token.totalSupply(), 1000000 * 10**18);
    }

    function testTransfer() public {
        vm.prank(owner);
        token.transfer(user1, 100);

        assertEq(token.balanceOf(user1), 100);
        assertEq(token.balanceOf(owner), token.totalSupply() - 100);
    }

    function testFailTransferInsufficientBalance() public {
        vm.prank(user1);
        token.transfer(user2, 100); // 应该失败
    }

    function testCannotTransferToZeroAddress() public {
        vm.prank(owner);
        vm.expectRevert("Invalid recipient");
        token.transfer(address(0), 100);
    }

    // 模糊测试
    function testFuzzTransfer(uint256 amount) public {
        vm.assume(amount > 0 && amount <= token.totalSupply());

        vm.prank(owner);
        token.transfer(user1, amount);

        assertEq(token.balanceOf(user1), amount);
    }

    // 使用 cheatcodes 测试
    function testDealAndPrank() public {
        // 给地址 ETH
        vm.deal(user1, 10 ether);

        // 模拟地址
        vm.prank(user1);

        // 测试功能
        assertEq(user1.balance, 10 ether);
    }

    // 主网分叉测试
    function testForkMainnet() public {
        vm.createSelectFork("https://eth-mainnet.alchemyapi.io/v2/...");

        // 与主网合约交互
        address dai = 0x6B175474E89094C44Da98b954EedeAC495271d0F;
        assertEq(IERC20(dai).symbol(), "DAI");
    }
}
```

## 高级测试模式

### 快照和回滚

```javascript
describe("Complex State Changes", function () {
  let snapshotId;

  beforeEach(async function () {
    snapshotId = await network.provider.send("evm_snapshot");
  });

  afterEach(async function () {
    await network.provider.send("evm_revert", [snapshotId]);
  });

  it("Test 1", async function () {
    // 进行状态变更
  });

  it("Test 2", async function () {
    // 状态已回滚，干净的状态
  });
});
```

### 主网分叉

```javascript
describe("Mainnet Fork Tests", function () {
  let uniswapRouter, dai, usdc;

  before(async function () {
    await network.provider.request({
      method: "hardhat_reset",
      params: [
        {
          forking: {
            jsonRpcUrl: process.env.MAINNET_RPC_URL,
            blockNumber: 15000000,
          },
        },
      ],
    });

    // 连接到现有的主网合约
    uniswapRouter = await ethers.getContractAt(
      "IUniswapV2Router",
      "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
    );

    dai = await ethers.getContractAt(
      "IERC20",
      "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    );
  });

  it("Should swap on Uniswap", async function () {
    // 使用真实的 Uniswap 合约测试
  });
});
```

### 模拟账户

```javascript
it("Should impersonate whale account", async function () {
  const whaleAddress = "0x...";

  await network.provider.request({
    method: "hardhat_impersonateAccount",
    params: [whaleAddress],
  });

  const whale = await ethers.getSigner(whaleAddress);

  // 使用大户的代币
  await dai
    .connect(whale)
    .transfer(addr1.address, ethers.utils.parseEther("1000"));
});
```

## Gas 优化测试

```javascript
const { expect } = require("chai");

describe("Gas Optimization", function () {
  it("Compare gas usage between implementations", async function () {
    const Implementation1 =
      await ethers.getContractFactory("OptimizedContract");
    const Implementation2 = await ethers.getContractFactory(
      "UnoptimizedContract",
    );

    const contract1 = await Implementation1.deploy();
    const contract2 = await Implementation2.deploy();

    const tx1 = await contract1.doSomething();
    const receipt1 = await tx1.wait();

    const tx2 = await contract2.doSomething();
    const receipt2 = await tx2.wait();

    console.log("Optimized gas:", receipt1.gasUsed.toString());
    console.log("Unoptimized gas:", receipt2.gasUsed.toString());

    expect(receipt1.gasUsed).to.be.lessThan(receipt2.gasUsed);
  });
});
```

## 覆盖率报告

```bash
# 生成覆盖率报告
npx hardhat coverage

# 输出显示：
# File                | % Stmts | % Branch | % Funcs | % Lines |
# -------------------|---------|----------|---------|---------|
# contracts/Token.sol |   100   |   90     |   100   |   95    |
```

## 合约验证

```javascript
// 在 Etherscan 上验证
await hre.run("verify:verify", {
  address: contractAddress,
  constructorArguments: [arg1, arg2],
});
```

```bash
# 或通过 CLI
npx hardhat verify --network mainnet CONTRACT_ADDRESS "Constructor arg1" "arg2"
```

## CI/CD 集成

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: "16"

      - run: npm install
      - run: npx hardhat compile
      - run: npx hardhat test
      - run: npx hardhat coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v2
```
