<template>
  <div class="page-container">
    <!-- Search bar -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" @submit.prevent>
        <el-form-item label="关键词">
          <el-input v-model="searchKeyword" placeholder="设备名称" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch"><el-icon><Search /></el-icon> 查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table -->
    <el-card shadow="never">
      <div class="table-header">
        <span class="table-title">端口互联</span>
        <el-button v-if="userStore.isAdmin" type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon> 新增
        </el-button>
      </div>
      <el-table :data="tableData" v-loading="loading" border stripe style="width: 100%" @row-dblclick="handleDetail">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="设备名称" min-width="160">
          <template #default="{ row }">
            <div class="device-name-cell">
              <span class="device-emoji">{{ deviceTypeEmoji(getDeviceType(row.asset_id)) }}</span>
              <span>{{ row.asset_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="port_count" label="物理端口数" width="100" />
        <el-table-column label="物理端口概况" min-width="180">
          <template #default="{ row }">
            <span v-if="row.ports_data && row.ports_data.length > 0">
              {{ getPortSummary(row.ports_data) }}
            </span>
            <span v-else class="text-muted">未配置</span>
          </template>
        </el-table-column>
        <el-table-column label="逻辑接口数" width="100">
          <template #default="{ row }">
            <span v-if="row.logical_interfaces && row.logical_interfaces.length > 0">
              {{ row.logical_interfaces.length }}
            </span>
            <span v-else class="text-muted">0</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            <span class="text-muted">{{ formatDateTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click.stop="handleDetail(row)">查看</el-button>
            <el-button v-if="userStore.isAdmin" size="small" link @click.stop="handleEdit(row)">编辑</el-button>
            <el-button v-if="userStore.isAdmin" size="small" type="danger" link @click.stop="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </el-card>

    <!-- Detail Drawer -->
    <el-drawer v-model="detailVisible" title="端口互联详情" size="65%">
      <div v-if="detailData" class="detail-body">
        <!-- Hero banner: device icon + name + type/brand (mirrors asset/index.vue detail-hero) -->
        <div class="detail-hero">
          <div class="detail-hero-icon" :style="{ background: deviceTypeColor(detailDeviceType) }">
            <span class="detail-hero-emoji">{{ deviceTypeEmoji(detailDeviceType) }}</span>
          </div>
          <div class="detail-hero-info">
            <div class="detail-hero-name">{{ detailData.asset_name || '—' }}</div>
            <div class="detail-hero-meta">
              <el-tag :color="deviceTypeColor(detailDeviceType)" effect="dark" size="small" round>
                {{ deviceTypeLabelFn(detailDeviceType) }}
              </el-tag>
              <span class="detail-hero-brand">{{ detailBrand || '未知品牌' }} · {{ detailModel || '型号未知' }}</span>
            </div>
          </div>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="物理端口数">{{ detailData.port_count }}</el-descriptions-item>
          <el-descriptions-item label="逻辑接口数">{{ (detailData.logical_interfaces || []).length }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ detailData.remark || '—' }}</el-descriptions-item>
        </el-descriptions>

        <!-- Logical interfaces detail -->
        <div v-if="detailData.logical_interfaces && detailData.logical_interfaces.length > 0">
          <div class="section-title">逻辑接口配置 ({{ detailData.logical_interfaces.length }} 个)</div>
          <el-table :data="detailData.logical_interfaces" border size="small">
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="row.type === 'vlanif' ? 'warning' : 'success'" size="small">
                  {{ row.type === 'vlanif' ? 'VLANIF' : 'ETH-TRUNK' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="接口名称" min-width="140" />
            <template v-if="hasVlanif(detailData.logical_interfaces)">
              <el-table-column label="VLAN ID" width="90">
                <template #default="{ row }">{{ row.type === 'vlanif' ? (row.vlan_id || '—') : '—' }}</template>
              </el-table-column>
              <el-table-column label="IP地址" min-width="130">
                <template #default="{ row }">{{ row.type === 'vlanif' ? (row.ip_address || '—') : '—' }}</template>
              </el-table-column>
              <el-table-column label="掩码" min-width="120">
                <template #default="{ row }">{{ row.type === 'vlanif' ? (row.mask || '—') : '—' }}</template>
              </el-table-column>
            </template>
            <template v-if="hasEthTrunk(detailData.logical_interfaces)">
              <el-table-column label="网络类型" width="100">
                <template #default="{ row }">
                  <span v-if="row.type === 'eth-trunk'">{{ NET_TYPE_LABEL[row.net_type] || 'Access' }}</span>
                  <span v-else>—</span>
                </template>
              </el-table-column>
              <el-table-column label="VLAN配置" min-width="130">
                <template #default="{ row }">
                  <span v-if="row.type === 'eth-trunk'">
                    <span v-if="row.net_type === 'access'">{{ row.vlan_id || '—' }}</span>
                    <span v-else>{{ row.vlan_range || '—' }}</span>
                  </span>
                  <span v-else>—</span>
                </template>
              </el-table-column>
              <el-table-column label="成员端口" min-width="200">
                <template #default="{ row }">
                  <span v-if="row.type === 'eth-trunk' && row.member_ports && row.member_ports.length > 0">
                    {{ row.member_ports.join(', ') }}
                  </span>
                  <span v-else>—</span>
                </template>
              </el-table-column>
            </template>
            <el-table-column prop="remark" label="备注" min-width="100" show-overflow-tooltip />
          </el-table>
        </div>

        <!-- Physical ports detail -->
        <div v-if="detailData.ports_data && detailData.ports_data.length > 0">
          <div class="section-title">物理端口配置 ({{ detailData.ports_data.length }} 个)</div>
          <el-table :data="detailPagedPorts" border size="small" style="width: 100%">
          <el-table-column prop="index" label="#" width="48" />
          <el-table-column prop="name" label="源接口" min-width="110" />
          <el-table-column label="本端网络类型" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="(detailBoundTrunk(row) ? detailBoundTrunk(row).net_type : row.net_type) === 'access' ? 'info' : ((detailBoundTrunk(row) ? detailBoundTrunk(row).net_type : row.net_type) === 'trunk' ? 'warning' : 'success')">
                {{ NET_TYPE_LABEL[detailBoundTrunk(row) ? detailBoundTrunk(row).net_type : row.net_type] || 'Access' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="VLAN" min-width="100">
            <template #default="{ row }">
              <template v-if="detailBoundTrunk(row)">
                <span v-if="detailBoundTrunk(row).net_type === 'access'">{{ detailBoundTrunk(row).vlan_id || '—' }}</span>
                <span v-else>{{ detailBoundTrunk(row).vlan_range || '—' }}</span>
              </template>
              <template v-else>
                <span v-if="row.net_type === 'access'">{{ row.vlan_id || '—' }}</span>
                <span v-else>{{ row.vlan_range || '—' }}</span>
              </template>
            </template>
          </el-table-column>
            <el-table-column prop="connected_device" label="目标设备" min-width="90" />
            <el-table-column prop="connected_interface" label="目标接口" min-width="90" />
            <el-table-column label="目标网络类型" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="(row.remote_net_type || 'access') === 'access' ? 'info' : ((row.remote_net_type || 'access') === 'trunk' ? 'warning' : 'success')">
                  {{ NET_TYPE_LABEL[row.remote_net_type] || 'Access' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="对端VLAN" min-width="100">
              <template #default="{ row }">
                <span v-if="(row.remote_net_type || 'access') === 'access'">{{ row.remote_vlan_id || '—' }}</span>
                <span v-else>{{ row.remote_vlan_range || '—' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'up' ? 'success' : 'info'" size="small">{{ row.status || '—' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="捆绑" width="100">
              <template #default="{ row }">
                <el-tag v-if="detailBoundTrunk(row)" type="success" size="small" effect="plain">捆绑 {{ detailBoundTrunk(row).name }}</el-tag>
                <span v-else class="text-muted">—</span>
              </template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" min-width="90" show-overflow-tooltip />
          </el-table>
          <div class="port-pager">
            <span class="port-pager-total">共 {{ detailData.ports_data.length }} 个端口</span>
            <el-pagination
              v-model:current-page="detailPortCurrentPage"
              v-model:page-size="detailPortPageSize"
              :total="detailData.ports_data.length"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next"
              background
              size="small"
              @current-change="() => {}"
              @size-change="() => { detailPortCurrentPage = 1 }"
            />
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- Add/Edit Drawer -->
    <el-drawer v-model="dialogVisible" :title="editingId ? '编辑端口互联' : '新增端口互联'" size="75%" :close-on-click-modal="false">
      <el-form label-width="100px">
        <el-form-item label="选择设备" required>
          <el-select
            v-model="selectedAssetId"
            placeholder="选择资产统计中的设备"
            filterable
            style="width: 300px"
            @change="onAssetChange"
          >
            <el-option
              v-for="asset in assetOptions"
              :key="asset.id"
              :label="`${asset.device_name} (${asset.device_type})`"
              :value="asset.id"
            />
          </el-select>
          <span v-if="portCount > 0" class="port-count-tag">
            <el-tag type="info" effect="plain">端口数: {{ portCount }}</el-tag>
          </span>
        </el-form-item>

        <el-form-item label="互联端口">
          <span v-if="ports.length > 0" class="port-summary">
            已根据资产端口配置自动生成 <b>{{ ports.length }}</b> 个端口（{{ portSummaryText }}）
          </span>
          <span v-else class="text-muted">请先在上方选择已配置端口的设备</span>
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="editForm.remark" type="textarea" :rows="2" placeholder="备注信息" style="width: 400px" />
        </el-form-item>
      </el-form>

      <!-- Logical Interface Section (placed above physical ports per requirement) -->
      <div v-if="ports.length > 0" class="port-section">
        <div class="port-section-title">
          <span>逻辑接口配置</span>
          <el-button size="small" type="primary" plain @click="addLogicalInterface">
            <el-icon><Plus /></el-icon> 添加逻辑接口
          </el-button>
        </div>
        <el-table v-if="logicalInterfaces.length > 0" :data="logicalInterfaces" border size="small" style="width: 100%">
          <el-table-column label="类型" width="140">
            <template #default="{ row }">
              <el-select v-model="row.type" size="small" @change="onLogicalTypeChange(row)">
                <el-option label="VLANIF接口" value="vlanif" />
                <el-option label="ETH-TRUNK接口" value="eth-trunk" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="接口名称" min-width="160">
            <template #default="{ row }">
              <el-input v-model="row.name" size="small" :placeholder="row.type === 'vlanif' ? '如：Vlanif10' : '如：Eth-Trunk1'" />
            </template>
          </el-table-column>
          <!-- VLANIF fields -->
          <el-table-column v-if="hasVlanif(logicalInterfaces)" label="VLAN ID" width="100">
            <template #default="{ row }">
              <el-input v-if="row.type === 'vlanif'" v-model="row.vlan_id" size="small" placeholder="如：10" />
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column v-if="hasVlanif(logicalInterfaces)" label="IP地址" min-width="150">
            <template #default="{ row }">
              <el-input v-if="row.type === 'vlanif'" v-model="row.ip_address" size="small" placeholder="如：192.168.10.1" />
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column v-if="hasVlanif(logicalInterfaces)" label="掩码" min-width="140">
            <template #default="{ row }">
              <el-input v-if="row.type === 'vlanif'" v-model="row.mask" size="small" placeholder="如：255.255.255.0" />
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <!-- ETH-TRUNK network config (maps down to bound physical ports, read-only there) -->
          <el-table-column v-if="hasEthTrunk(logicalInterfaces)" label="网络类型" width="120">
            <template #default="{ row }">
              <el-select v-if="row.type === 'eth-trunk'" v-model="row.net_type" size="small" style="width: 100%">
                <el-option label="Access" value="access" />
                <el-option label="Trunk" value="trunk" />
                <el-option label="Hybrid" value="hybrid" />
              </el-select>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column v-if="hasEthTrunk(logicalInterfaces)" label="VLAN配置" min-width="170">
            <template #default="{ row }">
              <template v-if="row.type === 'eth-trunk'">
                <el-input
                  v-if="row.net_type === 'access'"
                  v-model="row.vlan_id"
                  size="small"
                  placeholder="VLAN ID 如：10"
                />
                <el-input
                  v-else
                  v-model="row.vlan_range"
                  size="small"
                  placeholder="VLAN范围 如：10-20,100"
                />
              </template>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <!-- ETH-TRUNK member ports -->
          <el-table-column v-if="hasEthTrunk(logicalInterfaces)" label="成员端口（关联物理端口）" min-width="280">
            <template #default="{ row }">
              <el-select
                v-if="row.type === 'eth-trunk'"
                v-model="row.member_ports"
                size="small"
                multiple
                filterable
                collapse-tags
                collapse-tags-tooltip
                placeholder="选择物理端口"
                style="width: 100%"
                @change="onTrunkMembersChange(row)"
              >
                <el-option
                  v-for="port in ports"
                  :key="port.index"
                  :label="port.name || `端口${port.index}`"
                  :value="port.name || `端口${port.index}`"
                />
              </el-select>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="120">
            <template #default="{ row }">
              <el-input v-model="row.remark" size="small" placeholder="备注" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="70" fixed="right">
            <template #default="{ $index }">
              <el-button size="small" type="danger" link @click="removeLogicalInterface($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无逻辑接口，点击上方按钮添加" :image-size="60" />
      </div>

      <!-- Physical Port Table -->
      <div v-if="ports.length > 0" class="port-section">
        <div class="port-section-title">
          <span>物理端口配置 (共 {{ ports.length }} 个端口)</span>
          <el-input
            v-model="portSearchKeyword"
            size="small"
            clearable
            placeholder="搜索源接口筛选"
            style="width: 220px; margin-left: auto"
            @input="portCurrentPage = 1"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
        <el-table :data="pagedPorts" border size="small" style="width: 100%">
          <el-table-column prop="index" label="#" width="48" />
          <el-table-column label="源接口" min-width="120">
            <template #default="{ row }">
              <el-input v-model="row.name" size="small" :disabled="!!boundTrunk(row)" placeholder="如：GigabitEthernet0/0/1" />
            </template>
          </el-table-column>
          <!-- Network type: editable for all ports (bound ETH-TRUNK ports inherit trunk
               config as default via onTrunkMembersChange, but remain editable) -->
          <el-table-column label="本端网络类型" width="110">
            <template #default="{ row }">
              <el-select v-model="row.net_type" size="small" style="width: 100%">
                <el-option label="Access" value="access" />
                <el-option label="Trunk" value="trunk" />
                <el-option label="Hybrid" value="hybrid" />
              </el-select>
              <div v-if="boundTrunk(row)" class="sc-hint-mini">默认取 {{ boundTrunk(row).name }}</div>
            </template>
          </el-table-column>
          <!-- VLAN config: editable for all ports -->
          <el-table-column label="VLAN" min-width="140">
            <template #default="{ row }">
              <el-input
                v-if="row.net_type === 'access'"
                v-model="row.vlan_id"
                size="small"
                placeholder="VLAN ID 如：10"
              />
              <el-input
                v-else
                v-model="row.vlan_range"
                size="small"
                :placeholder="row.net_type === 'trunk' ? 'VLAN范围 如：10-20,100' : 'VLAN范围 如：10-20,100'"
              />
            </template>
          </el-table-column>
          <el-table-column label="目标设备" min-width="140">
            <template #default="{ row }">
              <el-select
                v-model="row.connected_device_id"
                size="small"
                filterable
                clearable
                :disabled="false"
                placeholder="选择对端设备"
                style="width: 100%"
                @change="(val) => onRemoteDeviceChange(row, val)"
              >
                <el-option
                  v-for="asset in remoteDeviceOptions(row)"
                  :key="asset.id"
                  :label="asset.device_name"
                  :value="asset.id"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="目标接口" min-width="140">
            <template #default="{ row }">
              <el-select
                v-model="row.connected_interface"
                size="small"
                filterable
                clearable
                :placeholder="row.connected_device_id ? '选择对端接口' : '请先选对端设备'"
                :disabled="!row.connected_device_id"
                style="width: 100%"
                @visible-change="(v) => v && loadRemotePorts(row.connected_device_id)"
              >
                <el-option
                  v-for="portName in remotePortOptions(row.connected_device_id)"
                  :key="portName"
                  :label="portName"
                  :value="portName"
                />
              </el-select>
            </template>
          </el-table-column>
          <!-- Peer port network type & VLAN (editable even when bound to ETH-TRUNK) -->
          <el-table-column label="目标网络类型" width="110">
            <template #default="{ row }">
              <el-select v-model="row.remote_net_type" size="small" style="width: 100%">
                <el-option label="Access" value="access" />
                <el-option label="Trunk" value="trunk" />
                <el-option label="Hybrid" value="hybrid" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="对端VLAN" min-width="140">
            <template #default="{ row }">
              <el-input
                v-if="(row.remote_net_type || 'access') === 'access'"
                v-model="row.remote_vlan_id"
                size="small"
                placeholder="VLAN ID 如：10"
              />
              <el-input
                v-else
                v-model="row.remote_vlan_range"
                size="small"
                placeholder="VLAN范围 如：10-20,100"
              />
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-select v-model="row.status" size="small" style="width: 90px">
                <el-option label="Up" value="up" />
                <el-option label="Down" value="down" />
                <el-option label="未连接" value="disconnected" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="100">
            <template #default="{ row }">
              <el-input v-model="row.remark" size="small" :disabled="!!boundTrunk(row)" placeholder="备注" />
            </template>
          </el-table-column>
          <el-table-column label="捆绑" width="110">
            <template #default="{ row }">
              <el-tag v-if="boundTrunk(row)" type="success" size="small" effect="plain">捆绑 {{ boundTrunk(row).name }}</el-tag>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
        </el-table>
        <div class="port-pager">
          <span class="port-pager-total">共 {{ filteredPorts.length }} 个端口{{ portSearchKeyword ? `（已筛选，全部 ${ports.length} 个）` : '' }}</span>
          <el-pagination
            v-model:current-page="portCurrentPage"
            v-model:page-size="portPageSize"
            :total="filteredPorts.length"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            background
            size="small"
            @current-change="() => {}"
            @size-change="() => { portCurrentPage = 1 }"
          />
        </div>
      </div>


      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getPortConnections, getPortConnection, getPortConnectionByAssetId, getReverseLinks, createPortConnection, updatePortConnection, deletePortConnection } from '@/api/port-connection'
import { getAssets } from '@/api/asset'
import { generatePorts, summarizePortGroups } from '@/utils/portNaming'

const userStore = useUserStore()
const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const searchKeyword = ref('')
const pagination = reactive({ page: 1, size: 20, total: 0 })

const dialogVisible = ref(false)
const editingId = ref(null)
const detailVisible = ref(false)
const detailData = ref(null)

// Form state
const selectedAssetId = ref(null)
const portCount = ref(0)
const ports = ref([])
const logicalInterfaces = ref([])
const editForm = reactive({ remark: '' })

// Physical port table pagination (selectable 10 / 20 / 50 / 100)
const portPageSize = ref(10)
const portCurrentPage = ref(1)
// Search keyword for filtering physical ports by source interface name (edit drawer only)
const portSearchKeyword = ref('')
// Sorted (UP first) + searched ports for the edit drawer physical port table
const filteredPorts = computed(() => {
  const statusWeight = (s) => (s === 'up' ? 0 : 1)
  const sorted = [...ports.value].sort((a, b) => {
    const d = statusWeight(a.status) - statusWeight(b.status)
    if (d !== 0) return d
    return (a.index || 0) - (b.index || 0)
  })
  const kw = (portSearchKeyword.value || '').trim().toLowerCase()
  if (!kw) return sorted
  return sorted.filter((p) => (p.name || '').toLowerCase().includes(kw))
})
const pagedPorts = computed(() => {
  const start = (portCurrentPage.value - 1) * portPageSize.value
  return filteredPorts.value.slice(start, start + portPageSize.value)
})

// Map physical port name -> owning ETH-TRUNK object (read-only binding display + inherited net config)
const portTrunkMap = computed(() => {
  const map = {}
  logicalInterfaces.value.forEach((li) => {
    if (li.type === 'eth-trunk' && Array.isArray(li.member_ports)) {
      li.member_ports.forEach((pn) => { map[pn] = li })
    }
  })
  return map
})
function boundTrunk(row) {
  return portTrunkMap.value[row.name] || null
}

// Detail-drawer equivalent (uses detailData's logical interfaces)
const detailPortTrunkMap = computed(() => {
  const map = {}
  ;(detailData.value?.logical_interfaces || []).forEach((li) => {
    if (li.type === 'eth-trunk' && Array.isArray(li.member_ports)) {
      li.member_ports.forEach((pn) => { map[pn] = li })
    }
  })
  return map
})
function detailBoundTrunk(row) {
  return detailPortTrunkMap.value[row.name] || null
}
const NET_TYPE_LABEL = { access: 'Access', trunk: 'Trunk', hybrid: 'Hybrid' }

// Detail drawer physical port pagination (default 10)
const detailPortPageSize = ref(10)
const detailPortCurrentPage = ref(1)
const detailPagedPorts = computed(() => {
  const all = detailData.value?.ports_data || []
  const start = (detailPortCurrentPage.value - 1) * detailPortPageSize.value
  return all.slice(start, start + detailPortPageSize.value)
})

// Asset options for dropdown
const assetOptions = ref([])

// Cache: remote device port lists (asset_id -> port names[])
const remotePortsCache = ref({})

async function loadAssets() {
  try {
    const data = await getAssets({ skip: 0, limit: 1000 })
    assetOptions.value = data.items || []
  } catch (err) {
    console.error('Failed to load assets:', err)
    assetOptions.value = []
  }
}

async function onAssetChange(assetId) {
  const asset = assetOptions.value.find(a => a.id === assetId)
  ports.value = []
  portSearchKeyword.value = ''
  if (!asset) return
  const portGroups = asset.extra_data?.port_groups || []
  const stackConfig = asset.extra_data?.stack_config || null
  const generated = generatePorts(portGroups, stackConfig)
  ports.value = generated.map((p, i) => ({
    index: i + 1,
    name: p.name,
    port_type: p.typeLabel,
    medium: p.medium,
    speed: p.speed,
    member: p.member,
    net_type: p.net_type || 'access',
    vlan_id: p.vlan_id || '',
    vlan_range: p.vlan_range || '',
    connected_device_id: null,
    connected_device: '',
    connected_interface: '',
    remote_net_type: 'access',
    remote_vlan_id: '',
    remote_vlan_range: '',
    status: 'disconnected',
    remark: '',
  }))
  // Fallback for devices without typed port config (non-switch / legacy)
  if (ports.value.length === 0) {
    const fb = Number(asset.extra_data?.port_count) || 8
    ports.value = Array.from({ length: fb }, (_, i) => ({
      index: i + 1,
      name: `端口${i + 1}`,
      port_type: '',
      medium: '',
      speed: '',
      member: null,
      net_type: 'access',
      vlan_id: '',
      vlan_range: '',
      connected_device_id: null,
      connected_device: '',
      connected_interface: '',
      remote_net_type: 'access',
      remote_vlan_id: '',
      remote_vlan_range: '',
      status: 'disconnected',
      remark: '',
    }))
  }
  portCount.value = ports.value.length
  portCurrentPage.value = 1

  // Auto-associate reverse interconnections: for each local port that has no manual
  // peer yet, look up whether another device already links TO this (device, port)
  // and prefill the peer device / interface / type / net / vlan accordingly.
  await autoFillReverseLinks()
}

/** Fetch reverse links for all current local ports and prefill peer info. */
async function autoFillReverseLinks() {
  const localPorts = ports.value.filter(p => !p.connected_device_id)
  if (localPorts.length === 0) return
  const names = localPorts.map(p => p.name)
  try {
    const links = await getReverseLinks(selectedAssetId.value, names)
    ports.value.forEach((p) => {
      const link = links && links[p.name]
      if (link && !p.connected_device_id) {
        p.connected_device_id = link.source_asset_id
        p.connected_device = link.source_asset_name
        p.connected_interface = link.source_port_name
        p.remote_net_type = link.source_net_type || 'access'
        p.remote_vlan_id = link.source_vlan_id || ''
        p.remote_vlan_range = link.source_vlan_range || ''
      }
    })
  } catch {
    // reverse-link lookup is best-effort; ignore failures
  }
}

/** Summary of generated ports by type, e.g. '千兆电口×24，万兆光口×4'. */
const portSummaryText = computed(() => {
  if (ports.value.length === 0) return ''
  const counts = {}
  ports.value.forEach((p) => {
    const key = p.port_type || '其他'
    counts[key] = (counts[key] || 0) + 1
  })
  return Object.entries(counts)
    .map(([k, v]) => `${k}×${v}`)
    .join('，')
})

// ---- Remote device port loading ----

/** Devices available for remote selection (exclude the current device) */
function remoteDeviceOptions(row) {
  return assetOptions.value.filter(a => a.id !== selectedAssetId.value)
}

/** When user selects a remote device, clear the interface and load its ports */
function onRemoteDeviceChange(row, deviceId) {
  row.connected_interface = ''
  const asset = assetOptions.value.find(a => a.id === deviceId)
  row.connected_device = asset ? asset.device_name : ''
  if (deviceId) {
    loadRemotePorts(deviceId)
  }
}

/** Load port names for a remote device (from its port-connection config) */
async function loadRemotePorts(deviceId) {
  if (!deviceId) return
  if (remotePortsCache.value[deviceId]) return // use cache

  try {
    const pcData = await getPortConnectionByAssetId(deviceId)
    // Physical ports + logical interfaces (Vlanif / Eth-Trunk)
    const portNames = [
      ...(pcData.ports_data || []).map(p => p.name),
      ...(pcData.logical_interfaces || []).filter(li => li.name).map(li => li.name),
    ].filter(n => n && n.trim())
    remotePortsCache.value[deviceId] = portNames
  } catch {
    // 404 = no port config for this device yet
    remotePortsCache.value[deviceId] = []
  }
}

/** Get port name options for a remote device */
function remotePortOptions(deviceId) {
  return remotePortsCache.value[deviceId] || []
}

// ---- Logical interfaces ----

function addLogicalInterface() {
  logicalInterfaces.value.push({
    type: 'vlanif',
    name: '',
    net_type: 'access',
    vlan_id: '',
    vlan_range: '',
    ip_address: '',
    mask: '',
    member_ports: [],
    remark: '',
  })
}

function removeLogicalInterface(index) {
  logicalInterfaces.value.splice(index, 1)
}

function onLogicalTypeChange(row) {
  // Clear type-specific fields when switching type, but preserve the relevant net config
  if (row.type === 'vlanif') {
    row.member_ports = []
    row.net_type = 'access'
    row.vlan_range = ''
  } else if (row.type === 'eth-trunk') {
    row.vlan_id = ''
    row.ip_address = ''
    row.mask = ''
    if (!row.net_type) row.net_type = 'access'
  }
}

/** When an ETH-TRUNK's member ports change, copy the trunk's net config down to the
 *  bound physical ports as their default. Ports remain individually editable afterwards. */
function onTrunkMembersChange(li) {
  const net = li.net_type || 'access'
  const vid = net === 'access' ? (li.vlan_id || '') : ''
  const vrange = net !== 'access' ? (li.vlan_range || '') : ''
  ;(li.member_ports || []).forEach((pn) => {
    const port = ports.value.find(p => p.name === pn)
    if (port) {
      port.net_type = net
      port.vlan_id = vid
      port.vlan_range = vrange
    }
  })
}

function hasVlanif(list) {
  return list.some(item => item.type === 'vlanif')
}

function hasEthTrunk(list) {
  return list.some(item => item.type === 'eth-trunk')
}

// ---- Asset meta helpers (lookup device_type / brand / model from cached assets) ----
const DEVICE_TYPE_COLOR = { switch: '#409eff', router: '#67c23a', firewall: '#f56c6c', security: '#e6a23c', other: '#909399' }
const DEVICE_TYPE_EMOJI = { switch: '🔀', router: '📡', firewall: '🛡', security: '🔒', other: '📦' }
const DEVICE_TYPE_LABEL_MAP = { switch: '交换机', router: '路由器', firewall: '防火墙', security: '安全设备', other: '其他' }

function findAsset(assetId) {
  return assetOptions.value.find((a) => a.id === assetId)
}
function getDeviceType(assetId) {
  return findAsset(assetId)?.device_type || ''
}
function getBrand(assetId) {
  return findAsset(assetId)?.brand || ''
}
function getModel(assetId) {
  return findAsset(assetId)?.model || ''
}
function deviceTypeColor(val) {
  return DEVICE_TYPE_COLOR[val] || '#909399'
}
function deviceTypeEmoji(val) {
  return DEVICE_TYPE_EMOJI[val] || '📦'
}
function deviceTypeLabelFn(val) {
  return DEVICE_TYPE_LABEL_MAP[val] || val || '未知'
}

// Detail-drawer hero meta (reactive — re-runs when assetOptions loads or detailData changes)
const detailDeviceType = computed(() => findAsset(detailData.value?.asset_id)?.device_type || '')
const detailBrand = computed(() => findAsset(detailData.value?.asset_id)?.brand || '')
const detailModel = computed(() => findAsset(detailData.value?.asset_id)?.model || '')

// ---- Helpers ----

function getPortSummary(portsData) {
  if (!portsData || portsData.length === 0) return '未配置'
  const connected = portsData.filter(p => p.connected_device).length
  return `${portsData.length} 端口, ${connected} 已互联`
}

function formatDateTime(val) {
  if (!val) return '—'
  const d = new Date(val)
  if (isNaN(d)) return val
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// ---- Data operations ----

async function fetchData() {
  loading.value = true
  try {
    const data = await getPortConnections({
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      keyword: searchKeyword.value || undefined,
    })
    tableData.value = data.items || []
    pagination.total = data.total || 0
  } catch (err) {
    console.error('Failed to fetch port connections:', err)
    tableData.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  searchKeyword.value = ''
  handleSearch()
}

function handleAdd() {
  editingId.value = null
  selectedAssetId.value = null
  portCount.value = 0
  ports.value = []
  portSearchKeyword.value = ''
  logicalInterfaces.value = []
  remotePortsCache.value = {}
  portCurrentPage.value = 1
  editForm.remark = ''
  loadAssets()
  dialogVisible.value = true
}

async function handleEdit(row) {
  editingId.value = row.id
  await loadAssets()
  selectedAssetId.value = row.asset_id
  portCount.value = row.port_count || 0
  portSearchKeyword.value = ''
  ports.value = (row.ports_data || []).map((p, i) => ({
    index: i + 1,
    name: p.name || `端口${i + 1}`,
    port_type: p.port_type || '',
    medium: p.medium || '',
    speed: p.speed || '',
    member: p.member || null,
    net_type: p.net_type || 'access',
    vlan_id: p.vlan_id || '',
    vlan_range: p.vlan_range || '',
    connected_device_id: p.connected_device_id || null,
    connected_device: p.connected_device || '',
    connected_interface: p.connected_interface || '',
    remote_net_type: p.remote_net_type || 'access',
    remote_vlan_id: p.remote_vlan_id || '',
    remote_vlan_range: p.remote_vlan_range || '',
    status: p.status || 'disconnected',
    remark: p.remark || '',
  }))
  portCurrentPage.value = 1
  logicalInterfaces.value = (row.logical_interfaces || []).map(li => ({
    type: li.type || 'vlanif',
    name: li.name || '',
    net_type: li.net_type || 'access',
    vlan_id: li.vlan_id || '',
    vlan_range: li.vlan_range || '',
    ip_address: li.ip_address || '',
    mask: li.mask || '',
    member_ports: li.member_ports || [],
    remark: li.remark || '',
  }))
  editForm.remark = row.remark || ''
  remotePortsCache.value = {}

  // Pre-load remote ports for all connected devices
  const deviceIds = [...new Set(ports.value.map(p => p.connected_device_id).filter(Boolean))]
  await Promise.all(deviceIds.map(id => loadRemotePorts(id)))

  // Also auto-associate any port that has no manual peer yet (reverse-link prefill)
  await autoFillReverseLinks()

  dialogVisible.value = true
}

async function handleDetail(row) {
  try {
    detailData.value = await getPortConnection(row.id)
  } catch {
    detailData.value = row
  }
  detailPortCurrentPage.value = 1
  detailVisible.value = true
}

async function handleSubmit() {
  if (!selectedAssetId.value) {
    ElMessage.warning('请选择设备')
    return
  }
  const asset = assetOptions.value.find(a => a.id === selectedAssetId.value)
  const payload = {
    asset_id: selectedAssetId.value,
    asset_name: asset?.device_name || '',
    port_count: portCount.value,
    ports_data: ports.value.map((p, i) => ({
      index: i + 1,
      name: p.name || `端口${i + 1}`,
      port_type: p.port_type || '',
      medium: p.medium || '',
      speed: p.speed || '',
      member: p.member || null,
      net_type: p.net_type || 'access',
      vlan_id: p.vlan_id || '',
      vlan_range: p.vlan_range || '',
      connected_device_id: p.connected_device_id || null,
      connected_device: p.connected_device || '',
      connected_interface: p.connected_interface || '',
      remote_net_type: p.remote_net_type || 'access',
      remote_vlan_id: p.remote_vlan_id || '',
      remote_vlan_range: p.remote_vlan_range || '',
      status: p.status || 'disconnected',
      remark: p.remark || '',
    })),
    logical_interfaces: logicalInterfaces.value.map(li => ({
      type: li.type || 'vlanif',
      name: li.name || '',
      net_type: li.type === 'eth-trunk' ? (li.net_type || 'access') : (li.net_type || 'access'),
      vlan_id: li.vlan_id || '',
      vlan_range: li.type === 'eth-trunk' ? (li.vlan_range || '') : '',
      ip_address: li.type === 'vlanif' ? (li.ip_address || '') : '',
      mask: li.type === 'vlanif' ? (li.mask || '') : '',
      member_ports: li.type === 'eth-trunk' ? (li.member_ports || []) : [],
      remark: li.remark || '',
    })),
    remark: editForm.remark || null,
  }
  submitting.value = true
  try {
    if (editingId.value) {
      await updatePortConnection(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createPortConnection(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (err) {
    ElMessage.error('操作失败: ' + (err?.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定要删除「${row.asset_name || 'ID:' + row.id}」的端口互联吗？`, '删除确认', { type: 'warning' })
  await deletePortConnection(row.id)
  ElMessage.success('删除成功')
  fetchData()
}

onMounted(() => {
  fetchData()
  loadAssets()
})
</script>

<style scoped>
.page-container { display: flex; flex-direction: column; gap: 16px; }
.search-card :deep(.el-card__body) { padding: 18px 20px 0 20px; }
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.table-title { font-size: 16px; font-weight: 600; }
.pagination { margin-top: 16px; justify-content: flex-end; }
.text-muted { color: var(--el-text-color-secondary); font-size: 13px; }
.port-count-tag { margin-left: 12px; }
.hint-text { margin-left: 12px; font-size: 12px; color: var(--el-text-color-secondary); }
.sc-hint-mini { font-size: 11px; color: var(--el-color-success); line-height: 1.3; margin-top: 2px; }
.detail-body { padding: 0 4px; display: flex; flex-direction: column; gap: 20px; }
.detail-body > div { min-width: 0; width: 100%; max-width: 100%; }
.section-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; }

/* ===== Device Name Icon (table column) ===== */
.device-name-cell { display: flex; align-items: center; gap: 6px; min-width: 0; }
.device-name-cell > span:last-child { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.device-emoji { font-size: 16px; }

/* ===== Detail Drawer Hero (icon + name + type/brand) ===== */
.detail-hero {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--el-bg-color-page);
  border-radius: 12px;
  padding: 18px 20px;
}
.detail-hero-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.detail-hero-emoji { font-size: 28px; }
.detail-hero-info { flex: 1; min-width: 0; }
.detail-hero-name {
  font-size: 18px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.detail-hero-meta { display: flex; align-items: center; gap: 8px; margin-top: 6px; flex-wrap: wrap; }
.detail-hero-brand { font-size: 13px; color: var(--el-text-color-secondary); }
.port-section { margin-top: 20px; }
.port-section-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; display: flex; align-items: center; gap: 12px; }
.port-pager { display: flex; align-items: center; justify-content: space-between; margin-top: 12px; gap: 12px; flex-wrap: wrap; }
.port-pager-total { font-size: 13px; color: var(--el-text-color-secondary); }
:deep(.el-table__row) { cursor: pointer; }

/* ===== Prevent table cell content from wrapping (use horizontal scroll for overflow) ===== */
:deep(.el-table .cell) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
:deep(.el-table .cell .el-tag) {
  white-space: nowrap;
}
:deep(.el-table) {
  display: block;
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
}
</style>
