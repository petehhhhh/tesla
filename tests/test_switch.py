"""Tests for the Tesla switch."""
from unittest.mock import patch

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_ON, SERVICE_TURN_OFF
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .common import setup_platform
from .mock_data import car as car_mock_data


async def test_registry_entries(hass: HomeAssistant) -> None:
    """Tests devices are registered in the entity registry."""
    await setup_platform(hass, SWITCH_DOMAIN)
    entity_registry = er.async_get(hass)

    entry = entity_registry.async_get("switch.my_model_s_heated_steering")
    assert entry.unique_id == f"{car_mock_data.VIN.lower()}_heated_steering"

    entry = entity_registry.async_get("switch.my_model_s_polling")
    assert entry.unique_id == f"{car_mock_data.VIN.lower()}_polling"

    entry = entity_registry.async_get("switch.my_model_s_charger")
    assert entry.unique_id == f"{car_mock_data.VIN.lower()}_charger"

    entry = entity_registry.async_get("switch.my_model_s_sentry_mode")
    assert entry.unique_id == f"{car_mock_data.VIN.lower()}_sentry_mode"


async def test_enabled_by_default(hass: HomeAssistant) -> None:
    """Tests devices are registered in the entity registry."""
    await setup_platform(hass, SWITCH_DOMAIN)
    entity_registry = er.async_get(hass)

    entry = entity_registry.async_get("switch.my_model_s_heated_steering")
    assert not entry.disabled

    entry = entity_registry.async_get("switch.my_model_s_polling")
    assert not entry.disabled

    entry = entity_registry.async_get("switch.my_model_s_charger")
    assert not entry.disabled

    entry = entity_registry.async_get("switch.my_model_s_sentry_mode")
    assert not entry.disabled


async def test_disabled_by_default(hass: HomeAssistant) -> None:
    """Tests devices are disabled by default when appropriate."""
    car_mock_data.VEHICLE_DATA["climate_state"]["steering_wheel_heater"] = None
    car_mock_data.VEHICLE_DATA["vehicle_state"]["sentry_mode_available"] = False
    await setup_platform(hass, SWITCH_DOMAIN)
    entity_registry = er.async_get(hass)

    entry = entity_registry.async_get("switch.my_model_s_heated_steering")
    assert entry.disabled

    entry = entity_registry.async_get("switch.my_model_s_sentry_mode")
    assert entry.disabled


async def test_heated_steering(hass: HomeAssistant) -> None:
    """Tests car heated steering switch."""
    car_mock_data.VEHICLE_DATA["climate_state"]["steering_wheel_heater"] = False
    await setup_platform(hass, SWITCH_DOMAIN)

    with patch(
        "teslajsonpy.car.TeslaCar.set_heated_steering_wheel"
    ) as mock_seat_heated_steering_wheel:
        # Test switch on
        assert await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: "switch.my_model_s_heated_steering"},
            blocking=True,
        )
        mock_seat_heated_steering_wheel.assert_awaited_once_with(True)
        # Test switch off
        assert await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: "switch.my_model_s_heated_steering"},
            blocking=True,
        )
        mock_seat_heated_steering_wheel.assert_awaited_with(False)


# async def test_polling(hass: HomeAssistant) -> None:
#     """Tests polling switch."""
#     await setup_platform(hass, SWITCH_DOMAIN)

#     with patch(
#         "teslajsonpy.Controller.set_updates"
#     ) as mock_controller_set_updates, patch("teslajsonpy.Controller.get_updates"):

#         assert await hass.services.async_call(
#             SWITCH_DOMAIN,
#             SERVICE_TURN_ON,
#             {ATTR_ENTITY_ID: "switch.my_model_s_polling"},
#             blocking=True,
#         )
#         mock_controller_set_updates.assert_awaited_once_with(car_mock_data.VIN, True)


async def test_charger(hass: HomeAssistant) -> None:
    """Tests car charger switch."""
    await setup_platform(hass, SWITCH_DOMAIN)

    with patch("teslajsonpy.car.TeslaCar.start_charge") as mock_start_charge:
        # Test switch on
        assert await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: "switch.my_model_s_charger"},
            blocking=True,
        )
        mock_start_charge.assert_awaited_once()

    with patch("teslajsonpy.car.TeslaCar.stop_charge") as mock_start_charge:
        # Test switch off
        assert await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: "switch.my_model_s_charger"},
            blocking=True,
        )
        mock_start_charge.assert_awaited()


async def test_sentry_mode(hass: HomeAssistant) -> None:
    """Tests car sentry mode switch."""
    car_mock_data.VEHICLE_DATA["vehicle_state"]["sentry_mode_available"] = True
    await setup_platform(hass, SWITCH_DOMAIN)

    with patch("teslajsonpy.car.TeslaCar.set_sentry_mode") as mock_set_sentry_mode:
        # Test switch on
        assert await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: "switch.my_model_s_sentry_mode"},
            blocking=True,
        )
        mock_set_sentry_mode.assert_awaited_once_with(True)
        # Test switch off
        assert await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: "switch.my_model_s_sentry_mode"},
            blocking=True,
        )
        mock_set_sentry_mode.assert_awaited_with(False)